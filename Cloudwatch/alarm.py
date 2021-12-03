import boto3
from botocore.exceptions import ClientError


class CloudWatch(object):
    def __init__(self, client) -> None:
        self.client = client

    def create_alarm(
        self, name: str, description: str, dimensions: list,
        comparison_op='GreaterThanOrEqualToThreshold', eval_period=1,
        metric_name='CPUUtilization', namespace='AWS/EC2', period=300,
        statistic='Average', threshold=70.0, actions_enabled=False,
        **kwargs
    ):
        """
        Create a cloudwatch metric based on the name.

        Example dimensions: [
            {
            'Name': 'InstanceId',
            'Value': '<INSTANCE_ID>'
            },
        ]
        """
        try:
            print(f'Creating the alarm: {name}')
            response = self.client.put_metric_alarm(
                AlarmName=name,
                ComparisonOperator=comparison_op,
                EvaluationPeriods=eval_period,
                MetricName=metric_name,
                Namespace=namespace,
                Period=period,
                Statistic=statistic,
                Threshold=threshold,
                ActionsEnabled=actions_enabled,
                AlarmDescription=description,
                Dimensions=dimensions
            )
            return response
        except ClientError as e:
            print(f'Error: Creating the alarm: {name}')
            print(e)

    def delete_alarms(self, alarm_names):
        """
        Delete the cloudwatch alarms.

        :param alarm_names: Provide the name of the alarm to delete it.
        :return: response json after performing the task.
        """
        try:
            if not isinstance(alarm_names, list):
                print("Bad parameter: alarm_names parameter is of type list.")
                raise
            response = self.client.delete_alarms(
                AlarmNames=alarm_names
            )
            return response
        except ClientError as e:
            print(e)
