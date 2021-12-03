## Install `boto3` python SDK.
```
pip install boto3
pip install awscli
```

## Configure your AWS programming credentials
Before using Boto3, you need to set up authentication credentials for your AWS account using either the IAM Console or the AWS CLI. You can either choose an existing user or create a new one.

**Steps to create AWS credentials through CLI**

`aws configure` -> Copy paste the credentials accordingly

**Add the credentials to the files at the same location mentioned below**

`~/.aws/credentials`

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

`~/.aws/config`

```
[default]
region=us-east-1
```

To configure extra details, look <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-a-configuration-file">here</a>