from typing import Optional
import pulumi
import pulumi_aws as aws

stack_name = pulumi.get_stack()
current = aws.get_caller_identity()
region = aws.get_region()

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
        versioning_configuration={
            "status": "Enabled"
        }
    )

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
        rules=[{
            "apply_server_side_encryption_by_default": {
                "sse_algorithm": "AES256"
            },
            "bucket_key_enabled": True
        }]
    )

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
        restrict_public_buckets=True
    )

def create_s3_bucket(
    name_prefix: str,
    versioning: bool,
    encryption: bool,
    public_access: bool,
    tags: Optional[dict]
) -> aws.s3.Bucket:
    """
    Creates an AWS S3 bucket with optional configurations for versioning, encryption, and public access.
    Args:
        name_prefix (str): Prefix for the bucket name.
        versioning (bool): If True, enables versioning on the bucket.
        encryption (bool): If True, enables encryption on the bucket.
        public_access (bool): If True, enables public access block on the bucket.
        tags (Optional[dict]): Dictionary of tags to assign to the bucket.
    Returns:
        aws.s3.Bucket: The created S3 bucket resource.
    """

    # Create a unique bucket name using account ID and region
    bucket_name = f"{name_prefix}-{current.account_id}-{region.name}"
    
    bucket = aws.s3.Bucket(
        f"{name_prefix}",
        bucket=bucket_name,
        tags=tags
    )
    
    # Apply optional configurations
    configurations = {
        versioning: enable_versioning,
        encryption: enable_encryption,
        public_access: enable_public_access_block,
    }
    
    for enabled, config_func in configurations.items():
        if enabled:
            config_func(bucket, name_prefix)
    
    return bucket
