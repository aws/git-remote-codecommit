#!/usr/bin/env python

import os
import setuptools

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
  name = 'git-remote-codecommit',
  packages = ['git_remote_codecommit'],
  version = '0.1',
  description = 'Git remote prefix to simplify pushing to and pulling from CodeCommit.',
  long_description = read('README.md'),
  author = 'Amazon Web Services',
  url = 'https://github.com/awslabs/git-remote-codecommit',
  license = 'Apache License 2.0',
  entry_points = {
    'console_scripts': [
      'git-remote-codecommit = git_remote_codecommit:main',
    ],
  },
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Utilities',
    'License :: OSI Approved :: Apache Software License',
  ],
)
