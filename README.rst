git-remote-codecommit
=====================

This package provides a simple method for pushing and pulling from `AWS
CodeCommit <https://aws.amazon.com/codecommit/>`__. This package extends `git
<https://git-scm.com/>`__ to support repository URLs prefixed with
**codecommit://**. For example, if using IAM...

::

  % cat ~/.aws/config
  [profile demo-profile]
  region = us-east-2
  output = json

  % cat ~/.aws/credentials
  [demo-profile]
  aws_access_key_id = AKIAIOSFODNN7EXAMPLE
  aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

... you can clone repositories as simply as...

::

  % git clone codecommit://demo-profile@MyRepositoryName

The *git-remote-codecommit* package works on Python versions:

* 3.6.x and greater
* 3.7.x and greater

Prerequisites
=============

Before you can use *git-remote-codecommit*, you must:

* Complete initial configuration for AWS CodeCommit, including:

  * Creating an AWS account
  * Configuring an IAM user or role
  * `Attaching a policy to that user/role that allows access to AWS CodeCommit repositories <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-identity-based-access-control.html#managed-policies>`__

* Create an AWS CodeCommit repository (or have one already) in your AWS account.
* Install Python and its package manager, pip, if they are not already installed. To download and install the latest version of Python, `visit the Python website <https://www.python.org/>`__.
* Install Git on your Linux, macOS, Windows, or Unix computer.
* Install the latest version of the AWS CLI on your Linux, macOS, Windows, or Unix computer. You can find instructions `here <https://docs.aws.amazon.com/cli/latest/userguide/installing.html>`__.

Note: Installation of the AWS CLI on some operating systems requires pip version 9.0.3 or later. To check your version of pip, open a terminal and type the following command:

::

  % pip --version

If the version is not 9.0.3 or later, run the following commands to update your version of pip:

::

  % curl -O https://bootstrap.pypa.io/get-pip.py
  % python3 get-pip.py --user

Set Up
===============

These instructions show how to set up *git-remote-codecommit* with an IAM user. If you plan to use a role with AWS Single Sign-On (SSO), see `this documentation <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html>`__ to help configure your named credential profiles. Once your profile is set up correctly, usage of the remote helper will be the same as if you were using an IAM user (skip to step 3).

Step 1: Look Up Your AWS Account ID and IAM User Access Key
-----------------------------------------------------------

* Look up and write down the account ID for your AWS account. You will need this information for step 2. If you don't know how to find your AWS Account ID, learn how `here <https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html>`__.

* Look up and write down the access key for your IAM user, if you do not already have that information stored locally. Learn more `here <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html>`__.

Step 2: `Configure an AWS credential profile <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html>`__ on your local computer
--------------------------------------------------------------------------------------------------------------------------------------------------

* On your local computer, run the **aws configure --profile** command to create an AWS CLI profile to use with *git-remote-codecommit*. When prompted, provide your AWS access key, your secret access key, the AWS Region where you created your AWS CodeCommit repository, and the default output format you prefer. For example:

::

  % aws configure --profile demo-profile
  AWS Access Key ID [None]: ***************
  AWS Secret Access Key [None]: ***************
  Default region name [None]: us-east-2
  Default output format [None]: json

Step 3: Install git-remote-codecommit
-------------------------------------

* On your Linux, macOS, Windows, or Unix computer, install *git-remote-codecommit* using the `pip <https://pip.pypa.io/en/latest/>`__ command. For example:

::

  % pip install git-remote-codecommit

* If you already have *git-remote-codecommit* installed you can upgrade to the latest version with the **--upgrade** parameter:

::

  % pip install --upgrade git-remote-codecommit

Step 4: Clone your repository
-----------------------------

* At the terminal, run the **git clone codecommit** command, using the name of your profile and the name of your repository. For example:

::

  % git clone codecommit://demo-profile@MyRepositoryName
  Cloning into 'MyRepositoryName'...
  remote: Counting objects: 1753, done.
  Receiving objects: 100% (1753/1753), 351.77 KiB | 1.91 MiB/s, done.
  Resolving deltas: 100% (986/986), done.

Usage
=====
*git-remote-codecommit* supports several different URL formats and variants with optional parameters.

RepositoryName is a required parameter. If you only supply this parameter, then *git-remote-codecommit* will attempt to use your default profile in the AWS Region configured in that profile. For example, to clone a repository named MyRepositoryName using the default profile:

::

  % git clone codecommit://MyRepositoryName

To specify a specific profile to use, use the profile name. For example, to clone a repository named *MyRepositoryName* using a profile named *demo-profile*:

::

  % git clone codecommit://demo-profile@MyRepositoryName

To specify an AWS Region different than the one in your profile, use the region parameter. For example, to clone a repository named *MyRepositoryName* in the *us-east-1* region using a profile named *demo-profile*:

::

  % git clone codecommit::us-east-1://demo-profile@MyRepositoryName

Getting Help
============
We use GitHub issues for tracking bugs and feature requests and have limited bandwidth to address them. We recommend using the following community resources for getting help:

* View the official setup steps for `HTTPS Connections to AWS CodeCommit with git-remote-codecommit <https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html>`__.
* Check our existing troubleshooting `documentation <https://docs.aws.amazon.com/codecommit/latest/userguide/troubleshooting-grc.html>`__ to see if your issue has been addressed there.
* Open a support ticket with `AWS Support <https://console.aws.amazon.com/support/home#/>`__.
* Check for an existing thread or start a new one on the `AWS CodeCommit forum <https://forums.aws.amazon.com/forum.jspa?forumID=189>`__.
* If you believe that you have found a bug, please `open an issue <https://github.com/aws/git-remote-codecommit/issues>`__.