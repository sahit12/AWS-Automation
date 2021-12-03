import boto3
import pprint
import json
from botocore.exceptions import ClientError


def check_group_exception(groupname):
    exception_groups = (
        'Admin',
        'UserAccess'
    )
    if groupname in exception_groups:
        return True
    else:
        return False


class Group:

    def __init__(self, client) -> None:
        self.client = client

    def create_group(self, group_name):
        try:
            response = self.client.create_group(
                GroupName=group_name
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Successfully created the group: {group_name}")
                return response
            else:
                print(f"There was an error creating the group: {group_name}")
            return response
        except ClientError as e:
            if 'EntityAlreadyExists' in str(e):
                return f"Group '{group_name}' already exists, provide a unique group name."

    def delete_group(self, group_name):
        try:
            if check_group_exception(groupname=group_name):
                raise BaseException(
                    f"You cannot remove the group: {group_name}")

            response = self.client.delete_group(
                GroupName=group_name
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Successfully deleted the group: {group_name}")
                return response
            else:
                print(f"There was an error deleting the group: {group_name}")
            return response
        except ClientError as e:
            return e

    def attach_group_policy(self,
                            group_name,
                            inline_policy_name=None,
                            inline_policy_document=None,
                            managed_policy_arn='arn:aws:iam::aws:policy/AWSDenyAll'):
        try:
            if check_group_exception(groupname=group_name):
                raise BaseException(
                    f"You cannot remove the group: {group_name}")

            if inline_policy_name:
                response = client.put_group_policy(
                    GroupName=group_name,
                    PolicyDocument=inline_policy_document,
                    PolicyName=inline_policy_name,
                )

            response = self.client.attach_group_policy(
                GroupName=group_name,
                PolicyArn=managed_policy_arn
            )
            policy_name = managed_policy_arn.split('/')[-1]
            print(
                f"Successfully Attached policy: {policy_name} to group: {group_name}")
            return response
        except ClientError as e:
            return e

    def delete_group_policy(self, group_name, policy_name):
        try:
            if check_group_exception(groupname=group_name):
                raise BaseException(
                    f"You cannot remove policy from the group: {group_name}")

            response = client.delete_group_policy(
                GroupName=group_name,
                PolicyName=policy_name,
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Successfully removed policy: {policy_name} from the group: {group_name}")
                return response
            else:
                print(f"There was an error removing policy: {policy_name} from the group: {group_name}")
            return response
        except ClientError as e:
            return e

    def remove_user_from_group(self, group_name, user):
        try:
            if check_group_exception(groupname=group_name):
                raise BaseException(
                    f"You are not allowed to perform operations on the group: {group_name}")

            response = self.client.remove_user_from_group(
                GroupName=group_name,
                UserName=user,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Successfully deleted user: {user} from the group: {group_name}")
                return response
            else:
                print(f"There was an error deleting user: {user} from the group: {group_name}")
            return response
        except ClientError as e:
            return e

    def add_user_to_group(self, group_name, user):
        try:
            if check_group_exception(groupname=group_name):
                raise BaseException(
                    f"You cannot add the user: {user} to the group: {group_name}")

            response = self.client.add_user_to_group(
                GroupName=group_name,
                UserName=user,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Successfully added user: {user} to the group: {group_name}")
                return response
            else:
                print(f"There was an error adding user: {user} to the group: {group_name}")
            return response
        except ClientError as e:
            return e


client = boto3.client('iam')

groupname = 'DemoGroup'

ex = Group(client=client)

# res = ex.create_group(groupname)
# pprint.pprint(res)

# res1 = ex.attach_group_policy(groupname)
# pprint.pprint(res1)

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:GetLaunchTemplateData",
                "ec2:TerminateInstances",
                "ec2:StartInstances",
                "ec2:CreateTags",
                "ec2:RunInstances",
                "ec2:StopInstances"
            ],
            "Resource": [
                "arn:aws:ec2:ap-south-1:*:volume/*",
                "arn:aws:ec2:ap-south-1:*:network-interface/*",
                "arn:aws:ec2:ap-south-1:*:instance/*",
                "arn:aws:ec2:ap-south-1:*:subnet/*",
                "arn:aws:ec2:ap-south-1:*:security-group/*",
                "arn:aws:ec2:ap-south-1::image/ami-052cef05d01020f1d "
            ],
            "Condition": {
                "StringEquals": {
                    "ec2:InstanceType": "t2.micro",
                    "ec2:Region": "ap-south-1"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DeleteVolume",
                "ec2:DeleteTags"
            ],
            "Resource": [
                "arn:aws:ec2:ap-south-1:*:volume/*",
                "arn:aws:ec2:ap-south-1:*:network-interface/*",
                "arn:aws:ec2:ap-south-1:*:instance/*",
                "arn:aws:ec2:ap-south-1:*:subnet/*",
                "arn:aws:ec2:ap-south-1:*:security-group/*",
                "arn:aws:ec2:ap-south-1::image/ami-052cef05d01020f1d "
            ],
            "Condition": {
                "StringEquals": {
                    "ec2:Region": "ap-south-1"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeTags",
                "ec2:DescribeVpcs",
                "ec2:GetEbsEncryptionByDefault",
                "ec2:DescribeVolumesModifications",
                "ec2:GetEbsDefaultKmsKeyId",
                "ec2:DescribeSubnets",
                "ec2:DescribeKeyPairs",
                "ec2:DescribeInstanceStatus"
            ],
            "Resource": "*"
        }
    ]
}
rs = ex.attach_group_policy(group_name=groupname, inline_policy_name='RunEC2Instances',
                            inline_policy_document=json.dumps(policy))
print(rs)
