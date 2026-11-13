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
import datetime
import os

from git_remote_codecommit import git_url, sign
from mock import Mock, patch

REGION = 'us-west-2'
TIMESTAMP = datetime.datetime(2017, 12, 24, 11, 53, 20)
CREDENTIAL = botocore.credentials.Credentials('access', 'secret')
CREDENTIAL_WITH_TOKEN = botocore.credentials.Credentials('access', 'secret', 'token')

EXPECTED_URL = 'https://access:20171224T115320Zb6df2d758a8023b2f000a546417007b65494f3ce8ad0300fd45fcfa173f1959a@git-codecommit.us-west-2.amazonaws.com/v1/repos/test_repo'
EXPECTED_URL_WITH_OVERRIDE = 'https://access:20171224T115320Za14a37a53035bbceb6e1748247b143124fe7326cdffd3d418236a592ce6158a0@land.called.honahlee/v1/repos/test_repo'
EXPECTED_URL_WITH_TOKEN = 'https://access%25token:20171224T115320Zb6df2d758a8023b2f000a546417007b65494f3ce8ad0300fd45fcfa173f1959a@git-codecommit.us-west-2.amazonaws.com/v1/repos/test_repo'
EXPECTED_SIG = '20171224T115320Zb6df2d758a8023b2f000a546417007b65494f3ce8ad0300fd45fcfa173f1959a'


def test_git_url_uses_one_refreshable_credential_generation():
  now = datetime.datetime.now(datetime.timezone.utc)
  generations = []

  def refresh():
    generation = str(len(generations) + 1)
    generations.append(generation)
    return dict(access_key='access' + generation, secret_key='secret' + generation,
                token='token' + generation, expiry_time=(now + datetime.timedelta(minutes=5)).isoformat())

  credentials = botocore.credentials.RefreshableCredentials(
      access_key='initial', secret_key='initial', token='initial',
      expiry_time=now + datetime.timedelta(minutes=5), refresh_using=refresh,
      method='test', time_fetcher=lambda: now)

  with patch('git_remote_codecommit.sign', return_value='signature') as signer:
    url = git_url('test_repo', 'v1', REGION, credentials)

  assert url == 'https://access1%25token1:signature@git-codecommit.us-west-2.amazonaws.com/v1/repos/test_repo'
  assert generations == ['1']
  signed_credentials = signer.call_args[0][3]
  assert signed_credentials.access_key == 'access1'
  assert signed_credentials.secret_key == 'secret1'
  assert signed_credentials.token == 'token1'


@patch('git_remote_codecommit.datetime.datetime', create = True)
def test_git_url(dt_mock):
  dt_mock.utcnow = Mock(return_value = TIMESTAMP)
  assert EXPECTED_URL == git_url('test_repo', 'v1', REGION, CREDENTIAL)


@patch.dict(os.environ, {'CODE_COMMIT_ENDPOINT': 'land.called.honahlee'})
@patch('git_remote_codecommit.datetime.datetime', create = True)
def test_git_url_with_override(dt_mock):
  dt_mock.utcnow = Mock(return_value = TIMESTAMP)
  assert EXPECTED_URL_WITH_OVERRIDE == git_url('test_repo', 'v1', REGION, CREDENTIAL)


@patch('git_remote_codecommit.datetime.datetime', create = True)
def test_git_url_with_token(dt_mock):
  dt_mock.utcnow = Mock(return_value = TIMESTAMP)
  assert EXPECTED_URL_WITH_TOKEN == git_url('test_repo', 'v1', REGION, CREDENTIAL_WITH_TOKEN)


@patch('git_remote_codecommit.datetime.datetime', create = True)
def test_sign(dt_mock):
  dt_mock.utcnow = Mock(return_value = TIMESTAMP)
  assert EXPECTED_SIG == sign('git-codecommit.us-west-2.amazonaws.com', '/v1/repos/test_repo', REGION, CREDENTIAL)
