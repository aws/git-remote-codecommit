#!/usr/bin/env python

import os
import setuptools
import distutils.cmd
from distutils import log
import subprocess
import operator
import six

__version__ = '1.0'


def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()


class CheckVersionTags(distutils.cmd.Command):

    description = "Make sure each release is tagged on GitHub"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if six.PY2:
            log.error("ERROR: This command is not compatible with Python 2")
            exit(1)

        url = "https://github.com/awslabs/git-remote-codecommit"
        ls_remote = subprocess.run(
            "git ls-remote " + url,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        lines = list(map(lambda s: str(s, encoding='utf-8'), ls_remote.stdout.splitlines()))
        tags = map(operator.methodcaller("split", "\t"), lines)
        matching_tags = list(filter(lambda t: t[1] == "refs/tags/" + __version__, tags))
        if len(matching_tags) == 0:
            log.error("ERROR: Version " + __version__ + " needs to be tagged in GitHub")
            exit(1)

        rev_parse = subprocess.run(
            "git rev-parse HEAD",
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        head_rev = str(rev_parse.stdout, encoding='utf-8').strip()
        if head_rev != matching_tags[0][0]:
            log.error(
                "ERROR: Tag " + matching_tags[0][1] + " is commit "
                + matching_tags[0][0] + " but this revision is "
                + head_rev
            )
            exit(1)


setuptools.setup(
    name = 'git-remote-codecommit',
    packages = ['git_remote_codecommit'],
    version = __version__,
    description = 'Git remote prefix to simplify pushing to and pulling from CodeCommit.',
    long_description = read('README.rst'),
    author = 'Amazon Web Services',
    url = 'https://github.com/awslabs/git-remote-codecommit',
    license = 'Apache License 2.0',
    install_requires = ['botocore >= 1.10.4'],
    setup_requires = ['six'],
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
    cmdclass = {
        'checkversiontags': CheckVersionTags
    }
)
