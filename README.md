# git-remote-codecommit

This package provides a simple method for pushing and pulling from [AWS CodeCommit](https://aws.amazon.com/codecommit/). This package extends [git](https://git-scm.com/) to support repository urls prefixed with **codecommit://**. For example, if using IAM...

```
% cat ~/.aws/config
[profile demo]
region = us-east-2
account = 111122223333

% cat ~/.aws/credentials
[demo]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

... you can clone repositories as simply as...

```
% git clone codecommit://my-profile@MyRepository
```

**Please be aware that this is a prototype / beta software. It is not ready for
general commercial release and may contain bugs, errors, or defects. It is
provided "AS IS."** We welcome users who want to give this a try and request
that you report any issues you encounter.

#Prerequisites
Before you can use git-remote-codecommit, you must:
+ Complete initial configuration for AWS CodeCommit, including creating an AWS account, configuring an IAM user with an access key ID and a secret access key associated with that IAM user, and attaching a policy (or equivalent permissions) to that user that allows access to AWS CodeCommit repositories. You can find instructions for these steps [here](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-https-unixes.html#setting-up-https-unixes-account).
+ Create an AWS CodeCommit repository, or have one already in your AWS account.
+ Install Git on your Linux, macOS, or Unix computer. (At this time, git-remote-codecommit is not compatible with Windows operating systems.)
+ Install the latest version of the AWS CLI on your Linux, macOS, or Unix computer. You can find instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/installing.html).



# Getting Started



## Step 1: Look Up Your AWS Account ID and IAM User Access Key

1. Look up and write down the account ID for your AWS account. You will need this information for git-remote-codecommit to work correctly. If you don't know how to find your AWS Account, ID, learn how [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html).
2. Look up and write down the access key for your IAM user, if you do not already have that information stored locally. Learn more [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

## Step 2: Configure AWS locally

1. On your local computer, run the **aws configure --profile** command to create an AWS CLI profile to use with git-remote-codecommit. For example:
```
aws configure --profile GRCProfile
```
When prompted, provide your AWS access key, your secret access key, the region where your AWS CodeCommit repository resides, and the default output format you prefer.

2. In a plain-text editor, open the config file, also known as the AWS CLI configuration file, and add your AWS account ID. Depending on your operating system, this file might be located at ~/.aws/config or some other location.
```
[profile GRCProfile]
region = us-east-2
account = 111122223333
```

3. Edit your  **~/.aws/credentials** file to verify that your access key and secret key are associated with your profile.
```
[GRCProfile]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

## Step 3: Install git-remote-codecommit

1. On your Linux, macOS, or Unix computer, install git-remote-codecommit using the  **pip** command. For example:
```
% sudo pip install git-remote-codecommit
```

2. If you already have git-remote-codecommit installed you can upgrade to the latest version with the **--upgrade** parameter:
```
% sudo pip install --upgrade git-remote-codecommit
```

## Step 4: Clone your repository

1. At the terminal, run the **git clone codecommit** command, using the name of your profile and the name of your repository. For example:
```
% git clone codecommit://GRCProfile@MyRepositoryName
Cloning into 'MyRepositoryName'...
warning: You appear to have cloned an empty repository.
Checking connectivity... done.
```

