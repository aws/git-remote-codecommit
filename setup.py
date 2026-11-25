#!/usr/bin/env python
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

import os
import setuptools

__version__ = '1.18'


def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name = 'git-remote-codecommit',
    packages = ['git_remote_codecommit'],
    version = __version__,
    description = 'Git remote prefix to simplify pushing to and pulling from CodeCommit.',
    long_description = read('README.rst'),
    author = 'Amazon Web Services',
    url = 'https://github.com/awslabs/git-remote-codecommit',
    license = 'Apache License 2.0',
    install_requires = ['botocore >= 1.29.75'],
    entry_points = {
        'console_scripts': [
            'git-remote-codecommit = git_remote_codecommit:main',
        ],
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
)
