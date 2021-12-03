## Amazon Elastic Container Registry (ECR)

* We can use lamdba functions to containerize it as a docker image and store it in ECR repository by creating a ECR repository and tagging the same docker repository to ECR newly created repository by the tag, so that it creates a direct mapping.

**General steps followed are below to create a docker container and push to ECR**
1. Authenticate the Docker CLI to your Amazon ECR registry
    
    `aws ecr get-login-password --region [ap-south-1] | docker login --username [username]--password-stdin [AWS account ID].dkr.ecr.[ap-south-1].amazonaws.com`

2. Create a repository in Amazon ECR using the **create-repository** command.

    `aws ecr create-repository --repository-name [hello-world] --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE`

3. Tag your image to match your repository name using the docker tag command.

    `docker tag  hello-world:latest [AWS account ID].dkr.ecr.[ap-south-1].amazonaws.com/hello-world:latest`

4. Deploy the image to Amazon ECR using the docker push command.

    `docker push [AWS account ID].dkr.ecr.[ap-south-1].amazonaws.com/hello-world:latest`

**Note**: The IAM user or role that creates the function should contain the AWS managed policies `GetRepositoryPolicy` and `SetRepositoryPolicy`.
Example: To create a role with the required policies, use below.
<pre>
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Sid": "VisualEditor0",
        "Effect": "Allow",
        "Action": ["ecr:SetRepositoryPolicy","ecr:GetRepositoryPolicy"],
        "Resource": "arn:aws:ecr:[region]:[account]:repository/[repo name]/"
        }
    ]
}
</pre>