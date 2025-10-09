"""
IAM Policy configurations for common AWS service access patterns.

This module contains predefined policy statements that can be used
with the create_custom_policy function for consistent IAM permissions.
"""

from typing import Dict, List, Any


# DynamoDB access policies
DYNAMODB_POLICIES = {
    "full_access": {
        "description": "Full CRUD access to DynamoDB table",
        "actions": [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Scan",
            "dynamodb:Query",
            "dynamodb:BatchGetItem",
            "dynamodb:BatchWriteItem",
        ]
    },
    "read_only": {
        "description": "Read-only access to DynamoDB table",
        "actions": [
            "dynamodb:GetItem",
            "dynamodb:Scan",
            "dynamodb:Query",
            "dynamodb:BatchGetItem",
        ]
    },
    "write_only": {
        "description": "Write-only access to DynamoDB table",
        "actions": [
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:BatchWriteItem",
        ]
    }
}

# S3 access policies
S3_POLICIES = {
    "full_access": {
        "description": "Full access to S3 bucket and objects",
        "actions": [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:GetObjectVersion",
            "s3:DeleteObjectVersion",
            "s3:PutObjectAcl",
            "s3:GetObjectAcl",
        ]
    },
    "read_only": {
        "description": "Read-only access to S3 bucket and objects",
        "actions": [
            "s3:GetObject",
            "s3:ListBucket",
            "s3:GetObjectVersion",
            "s3:GetObjectAcl",
        ]
    },
    "write_only": {
        "description": "Write-only access to S3 bucket and objects",
        "actions": [
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:DeleteObjectVersion",
            "s3:PutObjectAcl",
        ]
    },
    "list_only": {
        "description": "List-only access to S3 bucket",
        "actions": [
            "s3:ListBucket",
        ]
    }
}

# CloudWatch Logs policies
CLOUDWATCH_POLICIES = {
    "logs_write": {
        "description": "Write access to CloudWatch Logs",
        "actions": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
        ]
    }
}

# API Gateway policies
APIGATEWAY_POLICIES = {
    "invoke_lambda": {
        "description": "Allow API Gateway to invoke Lambda functions",
        "actions": [
            "lambda:InvokeFunction",
        ]
    }
}


def create_dynamodb_policy_statement(table_arn: str, access_level: str = "full_access") -> Dict[str, Any]:
    """
    Create a DynamoDB policy statement.
    
    Args:
        table_arn: ARN of the DynamoDB table
        access_level: Level of access ('full_access', 'read_only', 'write_only')
        
    Returns:
        IAM policy statement dictionary
    """
    if access_level not in DYNAMODB_POLICIES:
        raise ValueError(f"Invalid access level: {access_level}. Must be one of {list(DYNAMODB_POLICIES.keys())}")
    
    policy_config = DYNAMODB_POLICIES[access_level]
    
    return {
        "Effect": "Allow",
        "Action": policy_config["actions"],
        "Resource": table_arn,
    }


def create_s3_policy_statement(bucket_arn: str, access_level: str = "full_access") -> List[Dict[str, Any]]:
    """
    Create S3 policy statements (bucket and object access).
    
    Args:
        bucket_arn: ARN of the S3 bucket
        access_level: Level of access ('full_access', 'read_only', 'write_only', 'list_only')
        
    Returns:
        List of IAM policy statement dictionaries
    """
    if access_level not in S3_POLICIES:
        raise ValueError(f"Invalid access level: {access_level}. Must be one of {list(S3_POLICIES.keys())}")
    
    policy_config = S3_POLICIES[access_level]
    
    # For list_only, we only need bucket-level permissions
    if access_level == "list_only":
        return [{
            "Effect": "Allow",
            "Action": policy_config["actions"],
            "Resource": bucket_arn,
        }]
    
    # For other access levels, we need both bucket and object permissions
    statements = []
    
    # Bucket-level actions
    bucket_actions = [action for action in policy_config["actions"] if "Object" not in action]
    if bucket_actions:
        statements.append({
            "Effect": "Allow",
            "Action": bucket_actions,
            "Resource": bucket_arn,
        })
    
    # Object-level actions
    object_actions = [action for action in policy_config["actions"] if "Object" in action]
    if object_actions:
        statements.append({
            "Effect": "Allow",
            "Action": object_actions,
            "Resource": f"{bucket_arn}/*",
        })
    
    return statements


def create_cloudwatch_logs_policy_statement(log_group_arn: str = "*") -> Dict[str, Any]:
    """
    Create a CloudWatch Logs policy statement.
    
    Args:
        log_group_arn: ARN of the log group (defaults to all log groups)
        
    Returns:
        IAM policy statement dictionary
    """
    return {
        "Effect": "Allow",
        "Action": CLOUDWATCH_POLICIES["logs_write"]["actions"],
        "Resource": log_group_arn,
    }


def create_lambda_invoke_policy_statement(lambda_arn: str) -> Dict[str, Any]:
    """
    Create a Lambda invoke policy statement.
    
    Args:
        lambda_arn: ARN of the Lambda function
        
    Returns:
        IAM policy statement dictionary
    """
    return {
        "Effect": "Allow",
        "Action": ["lambda:InvokeFunction"],
        "Resource": lambda_arn,
    }