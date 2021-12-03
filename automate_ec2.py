import pprint
import boto3
from EC2.autoScaleUserData import encode_base64
from EC2.instance import EC2Instance
from EC2.instance import get_your_public_ip

data = '''
sudo apt-get update -y

sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg -y

echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y

sudo apt-get install docker-ce docker-ce-cli containerd.io -y
'''

if __name__ == '__main__':
    boot_file = 'docker/install_docker.sh'
    ec2 = EC2Instance(boto3.client('ec2'))
    ec2_r = EC2Instance(boto3.resource('ec2'))
    ec2_key = ec2.create_key_pair('default_key', False)
    ec2_dsg = ec2_r.setup_default_security_group('demo_sg', "Testing default", get_your_public_ip())
    ec2_ins = ec2.create_instances(
        key_name='default_key',
        image_id='ami-0567e0d2b4b2169ae',
        security_group_names=['demo_sg'],
        userdata=data
    )