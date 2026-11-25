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

# Regression test: a cross account assume-role profile whose source_profile
# authenticates through an [sso-session] section (the format written by
# `aws configure sso` in AWS CLI v2). botocore releases before 1.29.10 do not
# understand sso_session and fail with InvalidConfigError ("missing required
# configuration: sso_start_url, sso_region"). Releases 1.29.10 to 1.29.74 load
# the config but crash with AttributeError instead of asking for an SSO login
# when no token is cached, so the minimum is 1.29.75.

import botocore.exceptions
import botocore.session
import pytest

CONFIG = """
[profile jump]
sso_session = my-sso
sso_account_id = 111111111111
sso_role_name = Developer
region = eu-west-1

[sso-session my-sso]
sso_start_url = https://example.awsapps.com/start
sso_region = eu-west-1
sso_registration_scopes = sso:account:access

[profile cross-account]
role_arn = arn:aws:iam::222222222222:role/CodeCommitAccess
source_profile = jump
region = eu-west-1
"""


def test_assume_role_with_sso_session_source_profile(tmp_path, monkeypatch):
  config_file = tmp_path / 'config'
  config_file.write_text(CONFIG)
  monkeypatch.setenv('AWS_CONFIG_FILE', str(config_file))
  monkeypatch.setenv('AWS_SHARED_CREDENTIALS_FILE', str(tmp_path / 'credentials'))
  monkeypatch.setenv('HOME', str(tmp_path))  # empty SSO token cache
  for var in ('AWS_PROFILE', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN'):
    monkeypatch.delenv(var, raising = False)

  session = botocore.session.Session(profile = 'cross-account')

  # With no cached SSO token botocore must get as far as asking for an SSO
  # login, which proves the sso-session configuration was understood.
  # Assume-role credentials are deferred, so force the source profile to load.
  with pytest.raises(botocore.exceptions.SSOError):
    session.get_credentials().get_frozen_credentials()
