# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import collections
import datetime
import subprocess
import sys

import botocore.auth
import botocore.awsrequest
import botocore.compat
import botocore.hooks
import botocore.session

try:
  from urlparse import urlparse  # python 2.x
except ImportError:
  from urllib.parse import urlparse  # python 3.x

class FormatError(Exception):
  pass


class ProfileNotFound(Exception):
  pass


class RegionNotFound(Exception):
  pass


class CredentialsNotFound(Exception):
  pass


class Context(collections.namedtuple('Context', ['session', 'repository', 'version', 'region', 'credentials'])):
  """
  Repository information the hook concerns, derived from git's remote url and
  the user's AWS profile.

  :var botocore.session.Session session: aws session context
  :var str repository: repository name
  :var str version: protocol version for this hook
  :var str region: region the repository resides within
  :var botocore.credentials credentials: session credentials
  """

  @staticmethod
  def from_url(remote_url):
    """
    Parses repository information from a git url, filling in additional
    attributes we need from our AWS profile.

    Our remote helper accepts two distinct types of urls...

    * codecommit://<profile>@<repository>
    * codecommit::<region>://<profile>@<repository>

    If provided the former we get the whole url, but if the later git will
    truncate the proceeding 'codecommit::' prefix for us.

    The '<profile>@' url is optional, using the aws sessions present profile
    if not provided.

    :param str remote_url: git remote url to parse

    :returns: **Context** with our CodeCommit repository information

    :raises:
      * **FormatError** if the url is malformed
      * **ProfileNotFound** if the url references a profile that doesn't exist
      * **RegionNotFound** if the url references a region that doesn't exist
    """

    url = urlparse(remote_url)
    event_handler = botocore.hooks.HierarchicalEmitter()
    profile = 'default'
    repository = url.netloc
    region = url.scheme

    if not url.scheme or not url.netloc:
      raise FormatError("'%s' is a malformed url" % remote_url)

    if '@' in url.netloc:
      profile, repository = url.netloc.split('@', 1)
      session = botocore.session.Session(profile = profile, event_hooks = event_handler)

      if profile not in session.available_profiles:
        raise ProfileNotFound('Profile %s not found, available profiles are: %s' % (profile, ', '.join(session.available_profiles)))
    else:
      session = botocore.session.Session(event_hooks = event_handler)

    try:
      # when the aws cli is available support plugin authentication

      import awscli.plugin

      awscli.plugin.load_plugins(
        session.full_config.get('plugins', {}),
        event_hooks = event_handler,
        include_builtins = False,
      )

      session.emit_first_non_none_response('session-initialized', session = session)
    except ImportError:
      pass

    if url.scheme == 'codecommit':
      region = session.get_config_variable('region')

      if not region:
        raise RegionNotFound("Profile %s doesn't have a region available. Please set it." % profile)

    credentials = session.get_credentials()

    if not credentials:
      raise CredentialsNotFound("Profile %s doesn't have credentials available." % profile)

    return Context(session, repository, 'v1', region, credentials)


def error(msg):
  sys.stderr.write('%s\n' % msg)
  sys.exit(1)


def main():
  """
  Hook that can be invoked by git, providing simplified push/pull access for a
  CodeCommit repository.
  """

  if len(sys.argv) < 3:
    error('Too few arguments. This hook requires the git command and remote.')
  elif len(sys.argv) > 3:
    error("Too many arguments. Hook only accepts the git command and remote, but argv was: '%s'" % "', '".join(sys.argv))

  git_cmd, remote_url = sys.argv[1:3]

  try:
    context = Context.from_url(remote_url)
    authenticated_url = git_url(context.repository, context.version, context.region, context.credentials)
    sys.exit(subprocess.call(['git', 'remote-http', git_cmd, authenticated_url]))
  except (FormatError, ProfileNotFound, RegionNotFound, CredentialsNotFound) as exc:
    error(str(exc))


def git_url(repository, version, region, credentials):
  """
  Provides the signed url we can use for pushing and pulling from CodeCommit...

  ::

    https://(username):(password)@git-codecommit.(region).amazonaws.com/v1/repos/(repository)

  :param str repository: repository name
  :param str version: protocol version for this hook
  :param str region: region the repository resides within
  :param botocore.credentials credentials: session credentials

  :return: url we can push/pull from
  """

  hostname = 'git-codecommit.%s.amazonaws.com' % region
  path = '/%s/repos/%s' % (version, repository)

  token = '%' + credentials.token if credentials.token else ''
  username = botocore.compat.quote(credentials.access_key + token, safe='')
  signature = sign(hostname, path, region, credentials)

  return 'https://%s:%s@%s%s' % (username, signature, hostname, path)


def sign(hostname, path, region, credentials):
  """
  Provides a SigV4 signature for a CodeCommit url.

  :param str hostname: aws hostname request is for
  :param str path: resource the request is for
  :param str region: region the repository resides within
  :param botocore.credentials credentials: session credentials

  :return: signature for the url
  """

  request = botocore.awsrequest.AWSRequest(method = 'GIT', url = 'https://%s%s' % (hostname, path))
  request.context['timestamp'] = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')

  signer = botocore.auth.SigV4Auth(credentials, 'codecommit', region)
  canonical_request = 'GIT\n%s\n\nhost:%s\n\nhost\n' % (path, hostname)
  string_to_sign = signer.string_to_sign(request, canonical_request)
  signature = signer.signature(string_to_sign, request)
  return '%sZ%s' % (request.context['timestamp'], signature)
