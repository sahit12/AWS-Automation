## Important attributes of Lambda

### Function
This is the lambda function which is getting invoked to compute.

### Trigger
A trigger is a resource or configuration that invokes a Lambda function. Triggers include AWS services that you can configure to invoke a function and event source mappings. An event source mapping is a resource in Lambda that reads items from a stream or queue and invokes a function.

### Event
An event is a JSON-formatted document that contains data for a Lambda function to process. Example below.

<pre>
{
  "TemperatureK": 281,
  "WindKmh": -3,
  "HumidityPct": 0.55,
  "PressureHPa": 1020
}
</pre>

### Execution Environment
An execution environment provides a secure and isolated runtime environment for your Lambda function.
An execution environment manages the processes and resources that are required to run the function.

### Instruction set architecture
* arm64 – 64-bit ARM architecture, for the AWS Graviton2 processor.
* x86_64 – 64-bit x86 architecture, for x86-based processors.

### Deployment package
You deploy your Lambda function code using a deployment package. Lambda supports two types of
deployment packages:

* A `.zip` file archive that contains your function code and its dependencies. Lambda provides the operating system and runtime for your function.
* A container image that is compatible with the Open Container Initiative (OCI) specification. You add your function code and dependencies to the image. You must also include the `operating system` and a `Lambda runtime`.

### Runtime
The runtime provides a language-specific environment that runs in an execution environment. The runtime relays invocation events, context information, and responses between Lambda and the function. You can use runtimes that Lambda provides, or build your own. If you package your code as a .zip file archive, you must configure your function to use a runtime that matches your programming language. For a container image, you include the runtime when you build the image.

## Concurrency metrics
One can monitor concurrency levels in your account by using the following metrics:

* ConcurrentExecutions
* UnreservedConcurrentExecutions
* ProvisionedConcurrentExecutions
* ProvisionedConcurrencyInvocations
* ProvisionedConcurrencySpilloverInvocations
* ProvisionedConcurrencyUtilization

## Container images

* A container image includes the base operating system, the runtime, Lambda extensions, your application code and its dependencies. You can also add static data, such as machine learning models, into the image.
* Lambda provides a set of open-source base images that you can use to build your container image.
* To create and test container images, you can use the AWS Serverless Application Model (AWS SAM) command line interface (CLI) or native container tools such as the Docker CLI.
* You upload your container images to Amazon Elastic Container Registry (Amazon ECR), a managed AWS container image registry service. 
* To deploy the image to your function, you specify the Amazon ECR image URL using the Lambda console, the Lambda API, command line tools, or the AWS SDKs.

## .zip file archives

* A .zip file archive includes your application code and its dependencies. When you author functions using
the Lambda console or a toolkit, Lambda automatically creates a .zip file archive of your code.
* When you create functions with the Lambda API, command line tools, or the AWS SDKs, you must create a deployment package.
* You also must create a deployment package if your function uses a compiled language, or to add dependencies to your function.
* To deploy your function's code, you upload the deployment package from Amazon Simple Storage Service (Amazon S3) or your local machine.
* You can upload a .zip file as your deployment package using the Lambda console, AWS Command Line Interface (AWS CLI), or to an Amazon Simple Storage Service (Amazon S3) bucket.

## AWS managed policies for Lambda features

The following AWS managed policies provide permissions that are required to use Lambda features:

* `AWSLambdaBasicExecutionRole` – Permission to upload logs to CloudWatch.
* `AWSLambdaDynamoDBExecutionRole` – Permission to read records from an Amazon DynamoDB stream.
* `AWSLambdaKinesisExecutionRole` – Permission to read events from an Amazon Kinesis data stream or consumer.
* `AWSLambdaMQExecutionRole` – Permission to read records from an Amazon MQ broker.
* `AWSLambdaMSKExecutionRole` – Permission to read records from an Amazon Managed Streaming for Apache Kafka (Amazon MSK) cluster.
* `AWSLambdaSQSQueueExecutionRole` – Permission to read a message from an Amazon Simple Queue Service (Amazon SQS) queue.
* `AWSLambdaVPCAccessExecutionRole` – Permission to manage elastic network interfaces to connect your function to a virtual private cloud (VPC).
* `AWSXRayDaemonWriteAccess` – Permission to upload trace data to X-Ray.
* `CloudWatchLambdaInsightsExecutionRolePolicy` – Permission to write runtime metrics to CloudWatch Lambda Insights.
* `AmazonS3ObjectLambdaExecutionRolePolicy` – Permission to interact with Amazon S3 Object Lambda.