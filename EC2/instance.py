import boto3
import pprint
from requests import get


def get_your_public_ip():
    """
    Helper method to find your public IP.
    """
    ip = get('https://api.ipify.org').text
    return ip


class EC2Instance:
    def __init__(self, client) -> None:
        self.client = client

    def create_key_pair(self, KeyName, DryRun, **kwargs):
        """
        Creates a RSA key pair and saves the private key locally in the same folder.

        :params KeyName: A unique key name with which the public key file
                         will be used to store in AWS securely.
        :params DryRun: bool | This parameter will check if you have the permissions
                        to execute the current API. If yes, then it will respond with
                        "DryRunOperation" exception.
        :returns: Saves the private key.
        """
        try:
            response = self.client.create_key_pair(
                KeyName=str(KeyName),
                DryRun=DryRun
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                with open(KeyName + str(".pem"), 'w') as key_file:
                    key_file.write(response['KeyMaterial'])
                print(f'Private Key File created - {KeyName+str(".pem")}')
            return response
        except Exception as e:
            print(e)

    def delete_key_pair(self, keyname):
        """
        Deletes the Key pair from AWS

        :params keyname: Provide a valid key name to delete it from the AWS
        :returns: Response object
        """
        try:
            response = self.client.delete_key_pair(KeyName=keyname)
            return response
        except Exception as e:
            print(e)

    def describe_key_pairs(self):
        """
        Returns the key pairs available in AWS under the user account.
        """
        try:
            response = self.client.describe_key_pairs()
            return response
        except Exception as e:
            print(e)

    def describe_instances(self):
        """
        This API call provides you all the available EC2 instances being used.
        Note: The terminated instances will not show up.
        """
        try:
            response = self.client.describe_instances()
            return response

        except Exception as e:
            print(e)

    def setup_default_security_group(self, group_name, group_description, ssh_ingress_ip=None):
        """
        Creates a security group in the default virtual private cloud (VPC) of the
        current account, then adds rules to the security group to allow access to
        HTTP, HTTPS and, optionally, SSH.

        :param group_name: The name of the security group to create.
        :param group_description: The description of the security group to create.
        :param ssh_ingress_ip: The IP address that is granted inbound access to connect
                            to port 22 over TCP, used for SSH.
        :return: The newly created security group.
        """
        try:
            # Getting default VPC
            default_vpc = list(
                self.client.vpcs.filter(
                    Filters=[{'Name': 'isDefault', 'Values': ['true']}]
                )
            )[0]

            # Setting up security group in the default VPC
            security_group = default_vpc.create_security_group(
                GroupName=group_name,
                Description=group_description
            )
            print(
                f'Created security group {security_group} in the default VPC {default_vpc.id}')

            # Setting up inbound rules for the security group, if provided
            ip_permissions = [{
                # HTTP ingress open to anyone
                'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }, {
                # HTTPS ingress open to anyone
                'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }]
            if ssh_ingress_ip is not None:
                ip_permissions.append({
                    # SSH ingress open to only the specified IP address
                    'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
                    'IpRanges': [{'CidrIp': f'{ssh_ingress_ip}/32'}]})

            security_group.authorize_ingress(IpPermissions=ip_permissions)
            print("Setup complete for setting VPC.")
            return security_group
        except Exception as e:
            if str(e).__contains__('Duplicate'):
                print(
                    f"The security group '{group_name}' already exists for VPC '{group_description}'")

    def delete_security_group(self, group_name=None, group_id=None):
        """
        Deletes the security group. Either takes the group name or group ID and not both.

        :param group_name: The group name to delete
        :param group_id: The group ID to delete
        :return: The response json after creating the service.
        """
        try:
            if group_name:
                response = self.client.delete_security_group(
                    GroupName=group_name
                )
            elif group_id:
                response = self.client.delete_security_group(
                    GroupId=group_id
                )
            else:
                print(
                    "Invalid arguments passed, please provide either group name or group ID.")
            return response
        except Exception as e:
            if str(e).__contains__('EC2-Classic') or str(e).__contains__('DependencyViolation'):
                print(
                    f'The security group is already in use, please terminate the Ec2 instance first')

    def create_instances(self, key_name,
                         image_id='ami-041d6256ed0f2061c',
                         instance_type='t2.micro',
                         security_group_names=None
                         ):
        """
        Creates a new Amazon EC2 instance. The instance automatically starts immediately after
        it is created.

        The instance is created in the default VPC of the current account.

        :param image_id: The Amazon Machine Image (AMI) that defines the kind of
                        instance to create. The AMI defines things like the kind of
                        operating system, such as Amazon Linux, and how the instance is
                        stored, such as Elastic Block Storage (EBS).
        :param instance_type: The type of instance to create, such as 't2.micro'.
                            The instance type defines things like the number of CPUs and
                            the amount of memory.
        :param key_name: The name of the key pair that is used to secure connections to
                        the instance.
        :param security_group_names: A list of security groups that are used to grant
                                    access to the instance. When no security groups are
                                    specified, the default security group of the VPC
                                    is used.
        :return: The newly created instance.
        """
        try:
            if security_group_names:
                response = self.client.run_instances(
                    ImageId=image_id,
                    InstanceType=instance_type,
                    KeyName=key_name,
                    SecurityGroups=security_group_names,
                    MinCount=1,
                    MaxCount=1
                )
                print(f'Created EC2 instance {response[0].id}')
            else:
                response = self.client.run_instances(
                    ImageId=image_id,
                    InstanceType=instance_type,
                    KeyName=key_name,
                    MinCount=1,
                    MaxCount=1
                )
                print(f'Created EC2 instance {response[0].id}')
        except Exception as e:
            print(e)

    def stop_instances(self):
        try:
            # get the resource instance ID
            instance_id = self.describe_instances(
            )['Reservations'][0]['Instances'][0]['InstanceId']
            response = self.client.stop_instances(
                InstanceIds=[instance_id]
            )
            return response
        except Exception as e:
            print(e)

    def terminate_instance(self, instance_id):
        """
        Terminates an instance. The request returns immediately. To wait for the
        instance to terminate, use Instance.wait_until_terminated().
        :param instance_id: The ID of the instance to terminate.
        """
        try:
            response = self.client.Instance(instance_id).terminate()
            print(f'Terminating instance {instance_id}.')
            return response
        except Exception as e:
            print(e)


# ec2 = EC2Instance().describe_instances()
# ec2 = EC2Instance().stop_instances()
# ec2 = EC2Instance().create_key_pair(KeyName='demo_key', DryRun=False)
# ec2 = EC2Instance().delete_key_pair('demo_key')
# ec2 = EC2Instance().describe_key_pairs()
# ec2 = EC2Instance(boto3.resource('ec2')).setup_default_security_group(
#     'aws_py_test_sg',
#     'Testing EC2 security group',
#     get_your_public_ip()
# )
# ec2 = EC2Instance(boto3.client('ec2')).delete_security_group(group_name='aws_py_test_sg')
# pprint.pprint(ec2)
