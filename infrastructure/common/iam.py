import json
from typing import Any, Dict, List

import pulumi_aws as aws


def create_custom_policy(
    name_prefix: str, role: aws.iam.Role, policy_statements: List[Dict[str, Any]]
) -> aws.iam.RolePolicy:
    """
    Create a custom inline policy with provided statements.

    Args:
        name_prefix: Prefix for the policy name
        role: The IAM role to attach the policy to
        policy_statements: List of IAM policy statements

    Returns:
        The created role policy resource
    """
    policy_document = {"Version": "2012-10-17", "Statement": policy_statements}

    return aws.iam.RolePolicy(
        f"{name_prefix}-custom-policy",
        role=role.id,
        policy=json.dumps(policy_document),
    )
