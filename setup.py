#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = 'git-remote-codecommit',
  version = '1.0',
  descripion = 'Git remote prefix to simplify pushing to and pulling from CodeCommit.',
  author = 'Amazon Web Services',
  license = 'Apache License 2.0',
  packages = ['git_remote_codecommit'],
  entry_points = {
    'console_scripts': [
      'git-remote-codecommit = git_remote_codecommit:main',
    ],
  },
)
