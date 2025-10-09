from typing import Optional, List
import pulumi
import pulumi_aws as aws
import json
from policy_config import (
    create_dynamodb_policy_statement,
    create_s3_policy_statement,
    create_cloudwatch_logs_policy_statement
)
from common.iam import create_custom_policy

def create_lambda_execution_role(
    name_prefix: str,
    additional_policies: Optional[List[str]] = None,
    tags: Optional[dict] = None
) -> aws.iam.Role:
    """
    Create an IAM role for Lambda function execution with basic permissions.
    
    Args:
        name_prefix: Prefix for the role name
        additional_policies: List of additional managed policy ARNs to attach
        tags: Optional tags to apply to the role
        
    Returns:
        The created IAM role resource
    """
    # Create the trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
            "Effect": "Allow",
        }]
    }
    
    # Create the IAM role
    role = aws.iam.Role(
        f"{name_prefix}-role",
        assume_role_policy=json.dumps(trust_policy),
        tags=tags or {}
    )
    
    # Attach basic Lambda execution policy
    basic_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{name_prefix}-basic-policy",
        role=role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    
    # Attach any additional managed policies
    if additional_policies:
        for i, policy_arn in enumerate(additional_policies):
            aws.iam.RolePolicyAttachment(
                f"{name_prefix}-additional-policy-{i}",
                role=role.name,
                policy_arn=policy_arn,
            )
    
    return role


def create_dynamodb_policy(
    name_prefix: str,
    role: aws.iam.Role,
    table_arn: str,
    access_level: str = "full_access"
) -> aws.iam.RolePolicy:
    """
    Create an inline policy for DynamoDB access using predefined configurations.
    
    Args:
        name_prefix: Prefix for the policy name
        role: The IAM role to attach the policy to
        table_arn: ARN of the DynamoDB table (can be a Pulumi Output)
        access_level: Level of access ('full_access', 'read_only', 'write_only')
        
    Returns:
        The created role policy resource
    """
    def create_policy_doc(arn):
        statement = create_dynamodb_policy_statement(arn, access_level)
        return json.dumps({
            "Version": "2012-10-17",
            "Statement": [statement]
        })
    
    # If it's a Pulumi Output, use apply to transform it
    if isinstance(table_arn, pulumi.Output):
        policy_document = table_arn.apply(create_policy_doc)
    else:
        policy_document = create_policy_doc(table_arn)
    
    return aws.iam.RolePolicy(
        f"{name_prefix}-dynamodb-policy",
        role=role.id,
        policy=policy_document,
    )


def create_s3_policy(
    name_prefix: str,
    role: aws.iam.Role,
    bucket_arn: str,
    access_level: str = "full_access"
) -> aws.iam.RolePolicy:
    """
    Create an inline policy for S3 access using predefined configurations.
    
    Args:
        name_prefix: Prefix for the policy name
        role: The IAM role to attach the policy to
        bucket_arn: ARN of the S3 bucket (can be a Pulumi Output)
        access_level: Level of access ('full_access', 'read_only', 'write_only', 'list_only')
        
    Returns:
        The created role policy resource
    """
    def create_policy_doc(arn):
        statements = create_s3_policy_statement(arn, access_level)
        return json.dumps({
            "Version": "2012-10-17",
            "Statement": statements
        })
    
    # If it's a Pulumi Output, use apply to transform it
    if isinstance(bucket_arn, pulumi.Output):
        policy_document = bucket_arn.apply(create_policy_doc)
    else:
        policy_document = create_policy_doc(bucket_arn)
    
    return aws.iam.RolePolicy(
        f"{name_prefix}-s3-policy",
        role=role.id,
        policy=policy_document,
    )


def create_cloudwatch_logs_policy(
    name_prefix: str,
    role: aws.iam.Role,
    log_group_arn: str = "*"
) -> aws.iam.RolePolicy:
    """
    Create an inline policy for CloudWatch Logs access.
    
    Args:
        name_prefix: Prefix for the policy name
        role: The IAM role to attach the policy to
        log_group_arn: ARN of the log group (defaults to all log groups)
        
    Returns:
        The created role policy resource
    """
    statement = create_cloudwatch_logs_policy_statement(log_group_arn)
    
    return create_custom_policy(
        name_prefix=f"{name_prefix}-cloudwatch-logs",
        role=role,
        policy_statements=[statement]
    )
