import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pulumi
import pulumi_aws as aws

from common.s3 import create_s3_bucket
from common.dynamoDB import create_dynamodb_table
from api_gateway import create_lambda_rest_api
from iam_policies import create_lambda_execution_role, create_dynamodb_policy, create_s3_policy

def deploy_application_stack(stack_name: str):
    # Application Stack: Create the main infrastructure
    print(f"Deploying application infrastructure for stack: {stack_name}")
    
    # Create an S3 bucket for storing data/assets
    s3_resources = create_s3_bucket(
        name_prefix="api-bucket",
        versioning=True,
        encryption=True,
        public_access_block=True,
        tags={
            "Purpose": "App storage bucket",
            "Environment": stack_name,
            "ManagedBy": "Pulumi"
        }
    )
    
    # Create a DynamoDB table
    dynamodb_table = create_dynamodb_table(
        name_prefix="api-table",
        hash_key="id",
        attributes=[
            aws.dynamodb.TableAttributeArgs(
                name="id",
                type="S",
            ),
        ],
        tags={
            "Name": "API DynamoDB Table",
            "Environment": stack_name,
        },
    )
    
    # Create an IAM role for the Lambda function
    lambda_role = create_lambda_execution_role(
        name_prefix="lambda",
        tags={
            "Name": "Lambda Execution Role",
            "Environment": stack_name,
            "ManagedBy": "Pulumi"
        }
    )
    
    # Attach policy to allow Lambda to access DynamoDB
    # Options: 'full_access', 'read_only', 'write_only'
    dynamodb_policy = create_dynamodb_policy(
        name_prefix="lambda",
        role=lambda_role,
        table_arn=dynamodb_table.arn,
        access_level="full_access"  # Can be easily changed to 'read_only' or 'write_only'
    )
    
    # Attach policy to allow Lambda to access S3
    # Options: 'full_access', 'read_only', 'write_only', 'list_only'
    s3_policy = create_s3_policy(
        name_prefix="lambda",
        role=lambda_role,
        bucket_arn=s3_resources.bucket.arn,
        access_level="full_access"  # Can be easily changed to restrict access
    )
    
    # Create a Lambda function
    lambda_function = aws.lambda_.Function(
        "api-lambda",
        role=lambda_role.arn,
        runtime="python3.13",
        handler="app.handler",
        code=pulumi.AssetArchive({
            ".": pulumi.FileArchive("../src/lambda")
        }),
        environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "DYNAMODB_TABLE": dynamodb_table.name,
                "S3_BUCKET": s3_resources.bucket.id,
            },
        ),
        tags={
            "Name": "API Lambda Function",
            "Environment": stack_name,
        },
    )
    
    # Create REST API with Lambda integration
    api, stage, api_url = create_lambda_rest_api(
        name="api",
        lambda_function=lambda_function,
        stage_name=stack_name,
        description="Simple REST API with Lambda backend",
        enable_proxy_route=True,  # Enable catch-all {proxy+} route
        enable_root_route=True,   # Enable root / route
        tags={
            "Name": "Simple API",
            "Environment": stack_name,
            "ManagedBy": "Pulumi"
        }
    )
    
    # Export the API endpoint
    pulumi.export("api_url", api_url)
    pulumi.export("bucket_name", s3_resources.bucket.id,)
    pulumi.export("dynamodb_table_name", dynamodb_table.name)
    pulumi.export("lambda_function_name", lambda_function.name)

