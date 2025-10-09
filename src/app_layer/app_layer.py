import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pulumi
import pulumi_aws as aws
from common.config import _config
from common.s3 import create_s3_bucket
from common.dynamoDB import create_dynamodb_table
from iam_policies import create_lambda_execution_role, create_dynamodb_policy, create_s3_policy

def deploy_application_stack(stack_name: str):
    # Application Stack: Create the main infrastructure
    print(f"Deploying application infrastructure for stack: {stack_name}")
    
    # Create an S3 bucket for storing data/assets
    bucket = create_s3_bucket(
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
        bucket_arn=bucket.arn,
        access_level="full_access"  # Can be easily changed to restrict access
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
            "Environment": stack_name,
        },
    )
    
    # Create a REST API
    rest_api = aws.apigateway.RestApi(
        "api",
        description="Simple REST API",
        tags={
            "Name": "Simple API",
            "Environment": stack_name,
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
        stage_name=stack_name,
        tags={
            "Name": f"{stack_name.title()} Stage",
            "Environment": stack_name,
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
        _config.region_name,
        ".amazonaws.com/",
        stage.stage_name,
        "/",
    ))
    pulumi.export("bucket_name", bucket.id)
    pulumi.export("dynamodb_table_name", dynamodb_table.name)
    pulumi.export("lambda_function_name", lambda_function.name)

