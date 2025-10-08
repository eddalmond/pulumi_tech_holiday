"""
AWS Infrastructure for Simple API
This Pulumi program sets up:
- API Gateway
- Lambda function
- S3 bucket
- DynamoDB table
"""

import pulumi
import pulumi_aws as aws
import json

# Create an S3 bucket for storing data/assets
bucket = aws.s3.Bucket(
    "api-bucket",
    tags={
        "Name": "API Storage Bucket",
        "Environment": "dev",
    },
)

# Create a DynamoDB table
dynamodb_table = aws.dynamodb.Table(
    "api-table",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
    ],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": "API DynamoDB Table",
        "Environment": "dev",
    },
)

# Create an IAM role for the Lambda function
lambda_role = aws.iam.Role(
    "lambda-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
            "Effect": "Allow",
        }],
    }),
)

# Attach basic Lambda execution policy
lambda_role_policy = aws.iam.RolePolicyAttachment(
    "lambda-role-policy",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

# Attach policy to allow Lambda to access DynamoDB
dynamodb_policy = aws.iam.RolePolicy(
    "lambda-dynamodb-policy",
    role=lambda_role.id,
    policy=pulumi.Output.all(dynamodb_table.arn).apply(
        lambda args: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan",
                    "dynamodb:Query",
                ],
                "Resource": args[0],
            }],
        })
    ),
)

# Attach policy to allow Lambda to access S3
s3_policy = aws.iam.RolePolicy(
    "lambda-s3-policy",
    role=lambda_role.id,
    policy=pulumi.Output.all(bucket.arn).apply(
        lambda args: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                ],
                "Resource": [
                    args[0],
                    f"{args[0]}/*",
                ],
            }],
        })
    ),
)

# Create a Lambda function
lambda_function = aws.lambda_.Function(
    "api-lambda",
    role=lambda_role.arn,
    runtime="python3.12",
    handler="index.handler",
    code=pulumi.AssetArchive({
        "index.py": pulumi.StringAsset("""
import json
import os

def handler(event, context):
    \"\"\"
    Simple Lambda function that responds to API Gateway requests.
    Can be extended to interact with DynamoDB and S3.
    \"\"\"
    
    # Get environment variables
    table_name = os.environ.get('DYNAMODB_TABLE', 'Not configured')
    bucket_name = os.environ.get('S3_BUCKET', 'Not configured')
    
    # Parse the request
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    # Simple response
    response_body = {
        'message': 'Hello from Pulumi Lambda!',
        'path': path,
        'method': method,
        'dynamodb_table': table_name,
        's3_bucket': bucket_name,
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(response_body),
    }
"""),
    }),
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "DYNAMODB_TABLE": dynamodb_table.name,
            "S3_BUCKET": bucket.id,
        },
    ),
    tags={
        "Name": "API Lambda Function",
        "Environment": "dev",
    },
)

# Create a REST API
rest_api = aws.apigateway.RestApi(
    "api",
    description="Simple REST API",
    tags={
        "Name": "Simple API",
        "Environment": "dev",
    },
)

# Create a resource (path)
api_resource = aws.apigateway.Resource(
    "api-resource",
    rest_api=rest_api.id,
    parent_id=rest_api.root_resource_id,
    path_part="{proxy+}",
)

# Create a method for the resource
api_method = aws.apigateway.Method(
    "api-method",
    rest_api=rest_api.id,
    resource_id=api_resource.id,
    http_method="ANY",
    authorization="NONE",
)

# Create Lambda integration
api_integration = aws.apigateway.Integration(
    "api-integration",
    rest_api=rest_api.id,
    resource_id=api_resource.id,
    http_method=api_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function.invoke_arn,
)

# Create a method for the root resource
root_method = aws.apigateway.Method(
    "api-root-method",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="ANY",
    authorization="NONE",
)

# Create Lambda integration for root
root_integration = aws.apigateway.Integration(
    "api-root-integration",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method=root_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function.invoke_arn,
)

# Create a deployment
deployment = aws.apigateway.Deployment(
    "api-deployment",
    rest_api=rest_api.id,
    opts=pulumi.ResourceOptions(depends_on=[
        api_integration,
        root_integration,
    ]),
)

# Create a stage
stage = aws.apigateway.Stage(
    "api-stage",
    rest_api=rest_api.id,
    deployment=deployment.id,
    stage_name="dev",
    tags={
        "Name": "Development Stage",
        "Environment": "dev",
    },
)

# Grant API Gateway permission to invoke Lambda
lambda_permission = aws.lambda_.Permission(
    "api-lambda-permission",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="apigateway.amazonaws.com",
    source_arn=pulumi.Output.concat(rest_api.execution_arn, "/*/*"),
)

# Export the API endpoint
pulumi.export("api_url", pulumi.Output.concat(
    "https://",
    rest_api.id,
    ".execute-api.",
    aws.get_region().name,
    ".amazonaws.com/",
    stage.stage_name,
    "/",
))
pulumi.export("bucket_name", bucket.id)
pulumi.export("dynamodb_table_name", dynamodb_table.name)
pulumi.export("lambda_function_name", lambda_function.name)
