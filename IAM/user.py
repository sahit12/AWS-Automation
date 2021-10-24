import botocore
import boto3
import time
import pprint


class IAMUsers:
    def __init__(self, name='test') -> None:

        # Initialize an IAM client
        self.client = boto3.client('iam')
        self.name = name

    def create_user(self, user_name):
        try:
            _user_name = user_name if user_name else self.name
            response = self.client.create_user(
                UserName=_user_name,
                Tags=[
                    {
                        'Key': 'created_user',
                        'Value': str(time.time()) + "_" + _user_name,
                    },
                ]
            )
            return response

        except Exception as e:
            print(e)

    def update_user(self, current_username, new_username):
        try:
            _current_username = current_username if current_username else self.name
            response = self.client.update_user(
                UserName=_current_username,
                NewUserName=new_username
            )
            return response

        except Exception as e:
            print(e)

    def delete_user(self, username):
        try:
            _username = username if username else self.name
            response = self.client.delete_user(
                UserName=_username
            )
            return response

        except Exception as e:
            print(e)

    def list_users(self):
        try:
            response = self.client.list_users()
            return response

        except Exception as e:
            print(e)


#iam = IAMUsers().update_user('test1', 'DevUser')
# iam = IAMUsers().list_users()
# pprint.pprint(iam)
