import io
import boto3
import json
import time
import zipfile
from botocore.exceptions import ClientError


class LambdaAPI(object):

    def __init__(self, client) -> None:
        self.client = client

    def exponential_retry(self, func, error_code, *func_args, **func_kwargs):
        """
        Retries the specified function with a simple exponential backoff algorithm.
        This is necessary when AWS is not yet ready to perform an action because all
        resources have not been fully deployed.

        Credit: https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/lambda/boto_client_examples/lambda_handler_basic.py

        :param func: The function to retry.
        :param error_code: The error code to retry. Other errors are raised again.
        :param func_args: The positional arguments to pass to the function.
        :param func_kwargs: The keyword arguments to pass to the function.
        :return: The return value of the retried function.
        """
        sleepy_time = 1
        func_return = None
        while sleepy_time < 33 and func_return is None:
            try:
                func_return = func(*func_args, **func_kwargs)
                print(f'Ran {func.__name__}, got {func_return}.')
            except ClientError as error:
                if error.response['Error']['Code'] == error_code:
                    print(f'Sleeping for {sleepy_time} to give AWS time to connect resources.')
                    time.sleep(sleepy_time)
                    sleepy_time = sleepy_time*2
                else:
                    raise
        return func_return


    def create_zip_package(self, func_file_name):
        """
        Create a zip archive of the lambda function and also read the file as bytes

        :param func_file_name: The name of the file containing lambda handler function
        :return: return a byte representation of read file
        """
        try:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as ptr:
                ptr.write(func_file_name)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            print(e)

    def list_functions(self, **kwargs):
        """
        Returns a list of Lambda functions, with the version-specific configuration
        of each. Lambda returns up to 50 functions per call.

        :return: response containing every information of the functions

        """
        try:
            response = self.client.list_functions(
                FunctionVersion='ALL'
            )
            return response
        except ClientError as e:
            print(e)

    def create_iam_role_for_lambda(self, iam_resource, iam_role_name):
        """
        Creates an AWS Identity and Access Management (IAM) role that grants the
        AWS Lambda function basic permission to run. If a role with the specified
        name already exists, it is used for the demo.

        :param iam_resource: The Boto3 IAM resource object.
        :param iam_role_name: The name of the role to create.
        :return: The newly created role.
        """
        lambda_assume_role_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {
                        'Service': 'lambda.amazonaws.com'
                    },
                    'Action': 'sts:AssumeRole'
                }
            ]
        }
        policy_arn_basic = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        policy_arn_ec2 = 'arn:aws:iam::aws:policy/AmazonEC2FullAccess'

        try:
            role = iam_resource.create_role(
                RoleName=iam_role_name,
                AssumeRolePolicyDocument=json.dumps(lambda_assume_role_policy)
            )
            iam_resource.meta.client.get_waiter(
                'role_exists').wait(RoleName=iam_role_name)
            print(f'Created role {role.name}')

            role.attach_policy(PolicyArn=policy_arn_basic)
            role.attach_policy(PolicyArn=policy_arn_ec2)
            print(f'Attached basic execution policy to role {role.name}')

        except ClientError as error:
            if error.response['Error']['Code'] == 'EntityAlreadyExists':
                role = iam_resource.Role(iam_role_name)
                print(f'The role {iam_role_name} already exists. Using it.')
            else:
                print(f'Could not create role {iam_role_name} or attach policy')
                raise

        return role

    def deploy_lambda_function(self, function_name, description,
                               handler_name, iam_role, deployment_package, runtime='python3.9'):
        """
        Deploys the AWS Lambda function.

        :param function_name: The name of the AWS Lambda function.
        :param description: The description of the Lambda function.
        :param handler_name: The fully qualified name of the handler function. This
                            must include the file name and the function name.
        :param iam_role: The IAM role to use for the function.
        :param deployment_package: The deployment package that contains the function
                                code in ZIP format.
        :param runtime: The language specification to use during runtime.
        :return: The Amazon Resource Name (ARN) of the newly created function.
        """
        try:
            response = self.client.create_function(
                FunctionName=function_name,
                Description=description,
                Runtime=runtime,
                Role=iam_role.arn,
                Handler=handler_name,
                Code={'ZipFile': deployment_package},
                Publish=True
            )
            function_arn = response['FunctionArn']
            print(f"Created function '{function_name}' with ARN: '{function_arn}'.")
            return function_arn

        except ClientError as e:
            print(e)

    def delete_lambda_function(self, function_name):
        """
        Deletes an AWS Lambda function.
        
        :param function_name: The name of the function to delete.
        """
        try:
            self.client.delete_function(FunctionName=function_name)
        except ClientError:
            print(f'Could not delete function {function_name}.')
            raise

    def invoke_lambda_function(self, function_name, function_params):
        """
        Invokes an AWS Lambda function.
        
        :param function_name: The name of the function to invoke.
        :param function_params: The parameters of the function as a dict. This dict
                                is serialized to JSON before it is sent to AWS Lambda.
        :return: The response from the function invocation.
        """
        try:
            response = self.client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params).encode())
            print(f'Invoked function {function_name}.')
            return response
        except ClientError:
            print(f'Could not invoke function {function_name}.')
            raise

    def schedule_lambda_function(
        self, event_rule_name, event_schedule, lambda_function_name, lambda_function_arn):
        """
        Creates a schedule rule with Amazon EventBridge and registers an AWS Lambda
        function to be invoked according to the specified schedule.
        
        :param event_rule_name: The name of the scheduled event rule.
        :param event_schedule: The specified schedule in either cron or rate format.
        :param lambda_client: The Boto3 Lambda client.
        :param lambda_function_name: The name of the AWS Lambda function to invoke.
        :param lambda_function_arn: The Amazon Resource Name (ARN) of the function.
        :return: The ARN of the EventBridge rule.
        """
        eventbridge_client = boto3.client('events')
        try:
            response = eventbridge_client.put_rule(
                Name=event_rule_name, ScheduleExpression=event_schedule)
            event_rule_arn = response['RuleArn']
            print(f'Put rule {event_rule_name} with ARN {event_rule_arn}.')
        except ClientError:
            print(f'Could not put rule {event_rule_name}.')
            raise

        try:
            self.client.add_permission(
                FunctionName=lambda_function_name,
                StatementId=f'{lambda_function_name}-invoke',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=event_rule_arn)
            print(f'Granted permission to let Amazon EventBridge call function {lambda_function_name}')
        except ClientError:
            print(f'Could not add permission to let Amazon EventBridge call function {lambda_function_name}.')
            raise

        try:
            response = eventbridge_client.put_targets(
                Rule=event_rule_name,
                Targets=[{'Id': lambda_function_name, 'Arn': lambda_function_arn}])
            if response['FailedEntryCount'] > 0:
                print(f'Could not set {lambda_function_name} as the target for {event_rule_name}.')
            else:
                print(f'Set {lambda_function_name} as the target of {event_rule_name}.')
        except ClientError:
            print(f'Could not set {lambda_function_name} as the target of {event_rule_name}.')
            raise

        return event_rule_arn


    def update_event_rule(self, event_rule_name, enable):
        """
        Updates the schedule event rule by enabling or disabling it.
        
        :param event_rule_name: The name of the rule to update.
        :param enable: When True, the rule is enabled. Otherwise, it is disabled.
        """
        try:
            eventbridge_client = boto3.client('events')
            if enable:
                eventbridge_client.enable_rule(Name=event_rule_name)
            else:
                eventbridge_client.disable_rule(Name=event_rule_name)
            print(f'{event_rule_name} is now {"enabled" if enable else "disabled"}.')
        except ClientError:
            print(f'Could not {"enable" if enable else "disable"} {event_rule_name}.')
            raise


    def get_event_rule_enabled(self, event_rule_name):
        """
        Indicates whether the specified rule is enabled or disabled.
        
        :param event_rule_name: The name of the rule query.
        :return: True when the rule is enabled. Otherwise, False.
        """
        try:
            eventbridge_client = boto3.client('events')
            response = eventbridge_client.describe_rule(Name=event_rule_name)
            enabled = response['State'] == 'ENABLED'
            print(f'{event_rule_name} is {enabled}.')
        except ClientError:
            print(f'Could not get state of {event_rule_name}.')
            raise
        else:
            return enabled


    def delete_event_rule(self, event_rule_name, lambda_function_name):
        """
        Removes the specified targets from the event rule and deletes the rule.
        
        :param event_rule_name: The name of the rule to delete.
        :param lambda_function_name: The name of the AWS Lambda function to remove
                                    as a target.
        """
        try:
            eventbridge_client = boto3.client('events')
            eventbridge_client.remove_targets(
                Rule=event_rule_name, Ids=[lambda_function_name])
            eventbridge_client.delete_rule(Name=event_rule_name)
            print(f'Removed rule {event_rule_name}.')
        except ClientError:
            print(f'Could not remove rule {event_rule_name}.')
            raise


client = boto3.client('lambda')
iam_resource = boto3.resource('iam')

l = LambdaAPI(client=client)

lambda_function_filename = 'lambda_handler_scheduled.py'
lambda_handler_name = 'lambda_handler_scheduled.lambda_handler'
lambda_role_name = 'demo-lambda-role'
lambda_function_name = 'demo-lambda-scheduled'
event_rule_name = 'demo-event-scheduled'
event_schedule = 'cron(38 11 * * ? *)'


print(f"Creating AWS Lambda function {lambda_function_name} from the "
        f"{lambda_handler_name} function in {lambda_function_filename}...")
deployment_package = l.create_zip_package(lambda_function_filename)
iam_role = l.create_iam_role_for_lambda(iam_resource, lambda_role_name)
lambda_function_arn = l.exponential_retry(
    l.deploy_lambda_function, 'InvalidParameterValueException',
    lambda_function_name, 'Demo Lambda to Stop EC2 instance', lambda_handler_name, iam_role,
    deployment_package
)

print(f"Scheduling {lambda_function_name} to run as per cron job")
l.schedule_lambda_function(
    event_rule_name, event_schedule,
    lambda_function_name, lambda_function_arn
)

print(f"Sleeping for 3 minutes to let our function trigger...")
time.sleep(3*60)

print(f"Disabling event {event_rule_name}...")
l.update_event_rule(event_rule_name, False)
l.get_event_rule_enabled(event_rule_name)

print("Cleaning up all resources created for the demo...")
l.delete_event_rule(event_rule_name, lambda_function_name)
l.delete_lambda_function(lambda_function_name)
print(f"Deleted {lambda_function_name}.")

for policy in iam_role.attached_policies.all():
    policy.detach_role(RoleName=iam_role.name)
iam_role.delete()
print(f"Deleted {iam_role.name}.")
