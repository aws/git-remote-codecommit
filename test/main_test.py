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
import pytest
import sys

import git_remote_codecommit

from mock import Mock, patch

try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO


@patch('sys.stdout', new_callable = StringIO)
@patch('sys.stderr', new_callable = StringIO)
@patch('subprocess.call')
@patch('sys.exit', Mock(side_effect = KeyboardInterrupt('terminating')))
def assert_main(subprocess_mock, stderr_mock, stdout_mock, stdout = '', stderr = '', git_call = None):
  """
  Stubs out components of the main method that are troublesome for our tests,
  and asserts that its call matches these results.
  """

  def git_call_mock(args):
    assert git_call == ' '.join(args)

  subprocess_mock.side_effect = git_call_mock

  try:
    git_remote_codecommit.main()
  except KeyboardInterrupt:
    pass  # we use keyboard interrupts to mock exit calls, so accept those

  assert stdout == stdout_mock.getvalue()
  assert stderr == stderr_mock.getvalue()


@patch('git_remote_codecommit.Context.from_url', Mock())
@patch('git_remote_codecommit.git_url', Mock(return_value = 'https://test_url@codecommit/v1/repos/test_repo'))
@patch.object(sys, 'argv', ['git-remote-codecommit', 'clone', 'TestRepo'])
def test_main():
  assert_main(git_call = 'git remote-http clone https://test_url@codecommit/v1/repos/test_repo')


@patch.object(sys, 'argv', ['git-remote-codecommit'])
def test_main_with_too_few_arguments():
  assert_main(stderr = 'Too few arguments. This hook requires the git command and remote.\n')


@patch.object(sys, 'argv', ['git-remote-codecommit', 'arg1', 'arg2', 'arg3'])
def test_main_with_too_many_arguments():
  assert_main(stderr = "Too many arguments. Hook only accepts the git command and remote, but argv was: 'git-remote-codecommit', 'arg1', 'arg2', 'arg3'\n")


@patch.object(sys, 'argv', ['git-remote-codecommit', 'clone', 'TestRepo'])
def test_main_with_exceptions():
  # We check for quite a few issues. In those cases we provide a nice stderr message.

  recognized_exceptions = (
    git_remote_codecommit.FormatError,
    git_remote_codecommit.ProfileNotFound,
    git_remote_codecommit.RegionNotFound,
    git_remote_codecommit.CredentialsNotFound,
  )

  for exception_type in recognized_exceptions:
    with patch('git_remote_codecommit.Context.from_url', Mock(side_effect = exception_type('boom with a %s' % exception_type))):
      assert_main(stderr = 'boom with a %s\n' % exception_type)

  # .. however, if we encounter an error we don't expect the hook should still stacktrace.

  with patch('git_remote_codecommit.Context.from_url', Mock(side_effect = IOError('boom'))):
    with pytest.raises(IOError):
      assert_main()
