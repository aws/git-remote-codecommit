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

import botocore.credentials
import functools
import pytest

from git_remote_codecommit import Context, FormatError, ProfileNotFound, RegionNotFound, CredentialsNotFound
from mock import Mock, patch

DEFAULT_CREDS = botocore.credentials.Credentials('access_key', 'secret_key', 'token')


def mock_session(region = None, available_profiles = None, credentials = DEFAULT_CREDS):
  def decorator(func):
    session = Mock()
    session.get_config_variable.return_value = region
    session.available_profiles = available_profiles
    session.get_credentials.return_value = credentials

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
      with patch('botocore.session.Session', Mock(return_value = session)):
        with patch('awscli.plugin.load_plugins', Mock()):
          func(*args, **kwargs)

    return wrapped

  return decorator


@mock_session(region = 'us-west-2')
def test_without_profile():
  context = Context.from_url('codecommit://test_repo')
  assert 'test_repo' == context.repository
  assert 'v1' == context.version
  assert 'us-west-2' == context.region
  assert DEFAULT_CREDS == context.credentials


@mock_session(region = 'us-west-2', available_profiles = ['profile'])
def test_with_profile():
  context = Context.from_url('codecommit://profile@test_repo')
  assert 'test_repo' == context.repository
  assert 'v1' == context.version
  assert 'us-west-2' == context.region
  assert DEFAULT_CREDS == context.credentials


@mock_session()
def test_with_region():
  context = Context.from_url('ca-central-1://test_repo')
  assert 'test_repo' == context.repository
  assert 'v1' == context.version
  assert 'ca-central-1' == context.region
  assert DEFAULT_CREDS == context.credentials


@mock_session(available_profiles = ['profile'])
def test_with_profile_and_region():
  context = Context.from_url('ca-central-1://profile@test_repo')
  assert 'test_repo' == context.repository
  assert 'v1' == context.version
  assert 'ca-central-1' == context.region
  assert DEFAULT_CREDS == context.credentials


def test_with_malformed_url():
  malformed_urls = (
    '',
    'boom',
    'codecommit:/test_repo',    # missing a slash
    'codecommit//test_repo',    # missing colon
    '://test_repo',             # missing protocol
    'codecommit://',            # missing repository
    'codecommit:://test_repo',  # extra colon
    'codecommit:///test_repo',  # extra slash
  )

  for url in malformed_urls:
    with pytest.raises(FormatError):
      Context.from_url(url)


@mock_session(available_profiles = [])
def test_with_nonexistant_profile():
  with pytest.raises(ProfileNotFound):
    Context.from_url('codecommit://missing_profile@test_repo')


@mock_session(region = None)
def test_with_unset_region():
  with pytest.raises(RegionNotFound):
    Context.from_url('codecommit://test_repo')


@mock_session(region = 'us-west-2', credentials = None)
def test_without_credentials():
  with pytest.raises(CredentialsNotFound):
    Context.from_url('codecommit://test_repo')
