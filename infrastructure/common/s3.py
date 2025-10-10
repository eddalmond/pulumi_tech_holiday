from dataclasses import dataclass

import pulumi_aws as aws

from .config import _config


@dataclass
class S3BucketResources:
    """Container for all resources created by create_s3_bucket."""

    bucket: aws.s3.Bucket
    versioning: aws.s3.BucketVersioning | None = None
    encryption: aws.s3.BucketServerSideEncryptionConfiguration | None = None
    public_access_block: aws.s3.BucketPublicAccessBlock | None = None


def enable_versioning(bucket: aws.s3.Bucket, name_prefix: str):
    """
    Enables versioning on the specified AWS S3 bucket.

    Args:
        bucket (aws.s3.Bucket): The S3 bucket resource to enable versioning on.
        name_prefix (str): Prefix to use for naming the versioning resource.

    Returns:
        aws.s3.BucketVersioning: The Pulumi resource representing the bucket versioning configuration.
    """
    bucket_versioning = aws.s3.BucketVersioning(
        f"{name_prefix}-versioning",
        bucket=bucket.id,
        versioning_configuration={"status": "Enabled"},
    )
    return bucket_versioning


def enable_encryption(bucket: aws.s3.Bucket, name_prefix: str):
    """
    Enables server-side encryption for the specified AWS S3 bucket using AES256 algorithm.

    Args:
        bucket (aws.s3.Bucket): The S3 bucket resource to enable encryption on.
        name_prefix (str): Prefix to use for naming the encryption configuration resource.

    Returns:
        aws.s3.BucketServerSideEncryptionConfiguration: The encryption configuration resource.

    Note:
        This function configures bucket key enabled and applies AES256 encryption by default.
    """
    bucket_encryption = aws.s3.BucketServerSideEncryptionConfiguration(
        f"{name_prefix}-encryption",
        bucket=bucket.id,
        rules=[
            {
                "apply_server_side_encryption_by_default": {"sse_algorithm": "AES256"},
                "bucket_key_enabled": True,
            }
        ],
    )
    return bucket_encryption


def enable_public_access_block(bucket: aws.s3.Bucket, name_prefix: str):
    """
    Enables a public access block on the specified AWS S3 bucket to restrict public access.

    Args:
        bucket (aws.s3.Bucket): The S3 bucket resource to apply the public access block to.
        name_prefix (str): Prefix to use for naming the public access block resource.

    Returns:
        aws.s3.BucketPublicAccessBlock: The created public access block resource.

    The public access block will:
        - Block public ACLs
        - Block public bucket policies
        - Ignore public ACLs
        - Restrict public buckets
    """
    bucket_public_access_block = aws.s3.BucketPublicAccessBlock(
        f"{name_prefix}-pab",
        bucket=bucket.id,
        block_public_acls=True,
        block_public_policy=True,
        ignore_public_acls=True,
        restrict_public_buckets=True,
    )

    return bucket_public_access_block


def create_s3_bucket(
    name_prefix: str,
    versioning: bool,
    encryption: bool,
    public_access_block: bool,
    tags: dict | None,
) -> S3BucketResources:
    """
    Create an S3 bucket with optional security configurations.

    Args:
        name_prefix: Prefix for the bucket name
        versioning: Enable bucket versioning
        encryption: Enable server-side encryption
        public_access_block: Enable public access blocking
        tags: Optional tags to apply to the bucket

    Returns:
        S3BucketResources: Container with the bucket and all optional resources created
    """
    # Create a unique bucket name using account ID and region
    bucket_name = f"{name_prefix}-{_config.account_id}-{_config.region_name}"

    # Create the S3 bucket
    bucket = aws.s3.Bucket(f"{name_prefix}-bucket", bucket=bucket_name, tags=tags or {})

    # Create optional resources and track them
    versioning_resource = None
    encryption_resource = None
    public_access_block_resource = None

    if versioning:
        versioning_resource = enable_versioning(bucket, name_prefix)

    if encryption:
        encryption_resource = enable_encryption(bucket, name_prefix)

    if public_access_block:
        public_access_block_resource = enable_public_access_block(bucket, name_prefix)

    return S3BucketResources(
        bucket=bucket,
        versioning=versioning_resource,
        encryption=encryption_resource,
        public_access_block=public_access_block_resource,
    )
