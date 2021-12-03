import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('ec2')

def lambda_handler(event, context):
    logger.info(f'Event occured {event}')

    instance_ids = []

    try:
        instance_id = client.describe_instances(
            )['Reservations']
        for idx in instance_id:
            instance_ids.append(idx['Instances'][0]['InstanceId'])

        response = client.stop_instances(
            InstanceIds=instance_ids,
                DryRun=False
            )
        print(f'Stopped the instances - "{instance_ids}"')
    except Exception as e:
        print('Error occured during stopping instances.')
        raise
