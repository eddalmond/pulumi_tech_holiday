
import pulumi_aws as aws

from .config import _config


def create_dynamodb_table(
    name_prefix: str,
    hash_key: str,
    attributes: list | None = None,
    tags: dict | None = None,
) -> aws.dynamodb.Table:
    """
    Create a DynamoDB table for state locking.
    """
    dynamodb_table = aws.dynamodb.Table(
        f"{name_prefix}",
        name=f"{name_prefix}-{_config.account_id}",
        billing_mode="PAY_PER_REQUEST",
        hash_key=hash_key,
        attributes=attributes,
        tags=tags,
    )
    return dynamodb_table
