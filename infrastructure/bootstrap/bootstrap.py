import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pulumi
from common.config import _config
from common.dynamoDB import create_dynamodb_table
from common.s3 import create_s3_bucket


def deploy_bootstrap_stack():
    # Bootstrap Stack: Create S3 bucket and DynamoDB table for Pulumi state storage
    print("Deploying bootstrap infrastructure for state storage...")

    # Create the S3 bucket for storing Pulumi state
    state_bucket = create_s3_bucket(
        name_prefix="pulumi-state",
        versioning=True,
        encryption=True,
        public_access_block=True,
        tags={
            "Purpose": "Pulumi State Storage",
            "Environment": "Bootstrap",
            "ManagedBy": "Pulumi",
        },
    )

    # Create DynamoDB table for state locking
    lock_table = create_dynamodb_table(
        name_prefix="pulumi-state-lock",
        hash_key="LockID",
        attributes=[{"name": "LockID", "type": "S"}],
        tags={
            "Purpose": "Pulumi State Locking",
            "Environment": "Bootstrap",
            "ManagedBy": "Pulumi",
        },
    )

    # Export the values needed to configure other stacks
    pulumi.export("state_bucket_name", state_bucket.bucket)
    pulumi.export("state_bucket_region", _config.region_name)
    pulumi.export("lock_table_name", lock_table.name)
    pulumi.export("aws_account_id", _config.account_id)

    # Export the S3 backend configuration that other projects can use
    backend_config = {
        "bucket": state_bucket.bucket,
        "region": _config.region_name,
        "dynamodb_table": lock_table.name,
    }

    pulumi.export("backend_config", backend_config)

    # Export instructions for other projects
    instructions = pulumi.Output.all(state_bucket.bucket).apply(
        lambda args: f"""
To use this S3 backend in other Pulumi stacks:

1. Set the backend URL:
  pulumi login s3://{args[0]}

2. Or configure programmatically by adding this to your project's Pulumi.yaml:
  backend:
    url: s3://{args[0]}

3. The DynamoDB table will be used automatically for state locking.
"""
    )

    pulumi.export("usage_instructions", instructions)
