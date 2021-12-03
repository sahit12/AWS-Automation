import boto3
from botocore.exceptions import ClientError
import base64


def encode_base64(filepath):
    """
    Utility function to encode base64 string
    """
    try:
        with open(filepath, 'rb') as f_ptr:
            encoded_str = base64.b64encode(f_ptr.read())
            return encoded_str
    except Exception as e:
        print(e)


class AutoScaleUserData(object):
    def __init__(self, client) -> None:
        self.client = client

    def get_vpc_subnet_az(self):
        """
        Finds and returns the default VPC in the set region along with their
        subnet group ID and availabiltiy zone.
        """

        # Finding the default VPC ID
        try:
            response = self.client.describe_vpcs()
            for vpc in response['Vpcs']:
                if vpc['IsDefault'] == True:
                    vpc_id = vpc['VpcId']
                    break
            print(f'Found default VPC: {vpc_id}')
        except ClientError as e:
            print(e)

        # Find the subnet group ID and availability zone.
        try:
            response = self.client.describe_subnets()
            for sg in response['Subnets']:
                if sg['State'] == 'available':
                    sg_id = sg['SubnetId']
                    az = sg['AvailabilityZone']
                    break
            print(f'Found an available subnet ID: {sg_id}')
            return vpc_id, sg_id, az
        except ClientError as e:
            print(e)

    def create_ec2_security_group(self, sg_name, sg_description):
        """
        Create a security group in the default VPC

        :param sg_name: Provide a security group name to create it with.
        :param sg_description: Provide a security group description for creating it.
        :return: Security group ID and security group name
        """
        print('Creating the Security Group: {sg_name}')
        try:
            vpc_id, subnet_id, az = self.get_vpc_subnet_az()
            response = self.client.create_security_group(
                GroupName=sg_name,
                Description=sg_description,
                VpcId=vpc_id
            )

            security_grp_id = response["GroupId"]
            sg_config = self.client.authorize_security_group_ingress(
                GroupId=security_grp_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            print(
                'Creation of Security Group completed.\n Group ID: {security_grp_id}')
            return security_grp_id, sg_name

        except Exception as e:
            if str(e).__contains__("already exists"):
                response = self.client.describe_security_groups(GroupNames=[
                    sg_name])
                security_grp_id = response["SecurityGroups"][0]["GroupId"]
                print("Security Group {} already exists with Security Group ID: {} ".format(
                    sg_name, security_grp_id))
                return security_grp_id, sg_name

    def create_ec2_launch_template(self, template_name, key_pair, launch_file):
        """
        Creates an EC2 launch template for free tier instances.

        :param template_name: Provide unique name of the template to create it with.
        :param key_pair: EC2 key pair to securely connect to EC2 instance.
        :param launch_file: user data for launch configuration.
        :return: Template ID and Template Name
        """
        print(f'Creating the Launch Template: {template_name}')
        try:
            sg_id, sg_name = self.create_ec2_security_group()
            response = self.client.create_launch_template(
                LaunchTemplateName=template_name,
                LaunchTemplateData={
                    'ImageId': 'ami-08e0ca9924195beba',
                    'InstanceType': "t2.micro",
                    'KeyName': key_pair,
                    'UserData': encode_base64(launch_file),
                    'SecurityGroupIds': [sg_id]
                }
            )
            template_id = response['LaunchTemplate']['LaunchTemplateId']
            print(
                f'Creating the Launch Template created with Template ID:{template_id}')
            return template_id, template_name
        except Exception as e:
            response = self.client.describe_launch_templates(
                LaunchTemplateNames=[
                    template_name,
                ]
            )
            template_id = response['LaunchTemplates'][0]['LaunchTemplateId']
            return template_id, template_name

    def create_ec2_auto_scaling_group(self, auto_scaling_group_name):
        """
        Creates an autoscaling group which launches EC2 instances using lauch templates

        :param auto_scaling_group_name: Provide the name for auto scaling group
        :return: True | False
        """
        print("Creating the Auto Scaling Group using the Launch Template")
        launch_template_id, launch_template_name = self.create_ec2_launch_template()
        vpc_id, subnet_id, az = self.get_vpc_subnet_az()

        client = boto3.client('autoscaling')

        response = client.create_auto_scaling_group(
            AutoScalingGroupName='awspy_autoscaling_group',
            LaunchTemplate={
                'LaunchTemplateId': launch_template_id,
            },
            MinSize=1,
            MaxSize=2,
            DesiredCapacity=1,
            AvailabilityZones=[
                az,
            ]
        )

        if str(response["ResponseMetadata"]["HTTPStatusCode"]) == "200":
            print(
                'Successfully Created the Auto Scaling Group using Launch Templates')
            return True
        else:
            print(
                'Could not create the Auto Scaling Group using Launch Templates')
            return False
