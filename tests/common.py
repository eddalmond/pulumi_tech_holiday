"""
Common test utilities and mock classes for Pulumi infrastructure testing.

This module provides reusable mock classes and helper functions that can be
shared across all test modules in the test suite.
"""

from typing import Any

import pulumi


class PulumiTestMocks(pulumi.runtime.Mocks):
    """
    Comprehensive mock class for Pulumi infrastructure testing.

    This mock class provides realistic responses for AWS resources and
    provider calls commonly used in infrastructure code. It tracks created
    resources for verification in tests.

    Usage:
        from tests.common import PulumiTestMocks, setup_pulumi_mocks

        # In your test file
        setup_pulumi_mocks()

        # Or create custom instance
        mocks = PulumiTestMocks()
        pulumi.runtime.set_mocks(mocks, preview=False)
    """

    def __init__(self):
        self.created_resources: list[str] = []
        self.resource_outputs: dict[str, dict[str, Any]] = {}

    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        """
        Mock resource creation for various AWS resource types.

        Returns realistic mock outputs based on the resource type.
        """
        # Track what resources are being created
        self.created_resources.append(args.typ)

        outputs = args.inputs.copy()

        # S3 Bucket mocking
        if args.typ == "aws:s3/bucket:Bucket":
            bucket_name = args.inputs.get("bucket", args.name)
            outputs.update(
                {
                    "id": f"{bucket_name}-id",
                    "arn": f"arn:aws:s3:::{bucket_name}",
                    "bucket": bucket_name,
                    "region": "us-west-2",
                    "hosted_zone_id": "Z3AQBSTGFYJSTF",
                }
            )

        # S3 Bucket Versioning
        elif args.typ == "aws:s3/bucketVersioning:BucketVersioning":
            outputs.update(
                {
                    "id": f"{args.name}-id",
                    "bucket": args.inputs.get("bucket"),
                    "versioning_configuration": args.inputs.get(
                        "versioning_configuration", {}
                    ),
                }
            )

        # S3 Bucket Server Side Encryption Configuration
        elif (
            args.typ
            == "aws:s3/bucketServerSideEncryptionConfiguration:BucketServerSideEncryptionConfiguration"
        ):
            outputs.update(
                {
                    "id": f"{args.name}-id",
                    "bucket": args.inputs.get("bucket"),
                    "rules": args.inputs.get("rules", []),
                }
            )

        # S3 Bucket Public Access Block
        elif args.typ == "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock":
            outputs.update(
                {
                    "id": f"{args.name}-id",
                    "bucket": args.inputs.get("bucket"),
                    "block_public_acls": args.inputs.get("block_public_acls", True),
                    "block_public_policy": args.inputs.get("block_public_policy", True),
                    "ignore_public_acls": args.inputs.get("ignore_public_acls", True),
                    "restrict_public_buckets": args.inputs.get(
                        "restrict_public_buckets", True
                    ),
                }
            )

        # DynamoDB Table mocking
        elif args.typ == "aws:dynamodb/table:Table":
            table_name = args.inputs.get("name", args.name)
            outputs.update(
                {
                    "id": table_name,
                    "arn": f"arn:aws:dynamodb:us-west-2:123456789012:table/{table_name}",
                    "name": table_name,
                    "hash_key": args.inputs.get("hash_key"),
                    "range_key": args.inputs.get("range_key"),
                    "attributes": args.inputs.get("attributes", []),
                    "billing_mode": args.inputs.get("billing_mode", "PAY_PER_REQUEST"),
                }
            )

        # IAM Role mocking
        elif args.typ == "aws:iam/role:Role":
            role_name = args.inputs.get("name", args.name)
            outputs.update(
                {
                    "id": role_name,
                    "arn": f"arn:aws:iam::123456789012:role/{role_name}",
                    "name": role_name,
                    "assume_role_policy": args.inputs.get("assume_role_policy"),
                }
            )

        # IAM Role Policy mocking
        elif args.typ == "aws:iam/rolePolicy:RolePolicy":
            outputs.update(
                {
                    "id": f"{args.name}-id",
                    "role": args.inputs.get("role"),
                    "policy": args.inputs.get("policy"),
                }
            )

        # IAM Role Policy Attachment mocking
        elif args.typ == "aws:iam/rolePolicyAttachment:RolePolicyAttachment":
            outputs.update(
                {
                    "id": f"{args.name}-id",
                    "role": args.inputs.get("role"),
                    "policy_arn": args.inputs.get("policy_arn"),
                }
            )

        # Lambda Function mocking
        elif args.typ == "aws:lambda/function:Function":
            function_name = args.inputs.get("function_name", args.name)
            outputs.update(
                {
                    "id": function_name,
                    "arn": f"arn:aws:lambda:us-west-2:123456789012:function:{function_name}",
                    "function_name": function_name,
                    "runtime": args.inputs.get("runtime", "python3.13"),
                    "handler": args.inputs.get("handler"),
                    "role": args.inputs.get("role"),
                    "invoke_arn": f"arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:123456789012:function:{function_name}/invocations",
                }
            )

        # API Gateway REST API mocking
        elif args.typ == "aws:apigateway/restApi:RestApi":
            api_name = args.inputs.get("name", args.name)
            outputs.update(
                {
                    "id": f"{api_name}-api-id",
                    "name": api_name,
                    "description": args.inputs.get("description"),
                    "root_resource_id": f"{api_name}-root-id",
                    "execution_arn": f"arn:aws:execute-api:us-west-2:123456789012:{api_name}-api-id",
                }
            )

        # API Gateway Resource mocking
        elif args.typ == "aws:apigateway/resource:Resource":
            outputs.update(
                {
                    "id": f"{args.name}-resource-id",
                    "rest_api": args.inputs.get("rest_api"),
                    "parent_id": args.inputs.get("parent_id"),
                    "path_part": args.inputs.get("path_part"),
                    "path": args.inputs.get("path_part", ""),
                }
            )

        # API Gateway Method mocking
        elif args.typ == "aws:apigateway/method:Method":
            outputs.update(
                {
                    "id": f"{args.name}-method-id",
                    "rest_api": args.inputs.get("rest_api"),
                    "resource_id": args.inputs.get("resource_id"),
                    "http_method": args.inputs.get("http_method"),
                    "authorization": args.inputs.get("authorization", "NONE"),
                }
            )

        # API Gateway Integration mocking
        elif args.typ == "aws:apigateway/integration:Integration":
            outputs.update(
                {
                    "id": f"{args.name}-integration-id",
                    "rest_api": args.inputs.get("rest_api"),
                    "resource_id": args.inputs.get("resource_id"),
                    "http_method": args.inputs.get("http_method"),
                    "integration_http_method": args.inputs.get(
                        "integration_http_method"
                    ),
                    "type": args.inputs.get("type"),
                    "uri": args.inputs.get("uri"),
                }
            )

        # API Gateway Deployment mocking
        elif args.typ == "aws:apigateway/deployment:Deployment":
            outputs.update(
                {
                    "id": f"{args.name}-deployment-id",
                    "rest_api": args.inputs.get("rest_api"),
                    "triggers": args.inputs.get("triggers", {}),
                }
            )

        # API Gateway Stage mocking
        elif args.typ == "aws:apigateway/stage:Stage":
            stage_name = args.inputs.get("stage_name", args.name)
            rest_api_id = args.inputs.get("rest_api", "mock-api-id")
            outputs.update(
                {
                    "id": f"{rest_api_id}/{stage_name}",
                    "rest_api": rest_api_id,
                    "deployment": args.inputs.get("deployment"),
                    "stage_name": stage_name,
                    "invoke_url": f"https://{rest_api_id}.execute-api.us-west-2.amazonaws.com/{stage_name}",
                }
            )

        # Lambda Permission mocking
        elif args.typ == "aws:lambda/permission:Permission":
            outputs.update(
                {
                    "id": f"{args.name}-permission-id",
                    "function_name": args.inputs.get("function_name"),
                    "action": args.inputs.get("action", "lambda:InvokeFunction"),
                    "principal": args.inputs.get("principal"),
                    "source_arn": args.inputs.get("source_arn"),
                }
            )

        # Generic fallback for other resource types
        else:
            outputs.update(
                {
                    "id": f"{args.name}-id",
                }
            )

        # Store outputs for potential inspection
        self.resource_outputs[args.name] = outputs

        return [f"{args.name}-id", outputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        """
        Mock AWS provider calls for data sources and functions.
        """
        if args.token == "aws:index/getCallerIdentity:getCallerIdentity":
            return {
                "accountId": "123456789012",
                "arn": "arn:aws:iam::123456789012:user/test-user",
                "userId": "AIDACKCEVSQ6C2EXAMPLE",
            }
        elif args.token == "aws:index/getRegion:getRegion":
            return {
                "name": "us-west-2",
                "description": "US West (Oregon)",
            }
        elif args.token == "aws:index/getAvailabilityZones:getAvailabilityZones":
            return {
                "names": ["us-west-2a", "us-west-2b", "us-west-2c"],
                "zone_ids": ["usw2-az1", "usw2-az2", "usw2-az3"],
            }
        return {}

    def reset_tracking(self):
        """Reset the tracked resources list between tests."""
        self.created_resources = []
        self.resource_outputs = {}

    def get_created_resources(self) -> list[str]:
        """Get list of all resource types that were created."""
        return self.created_resources.copy()

    def get_resource_output(self, resource_name: str) -> dict[str, Any]:
        """Get the mock outputs for a specific resource."""
        return self.resource_outputs.get(resource_name, {})

    def was_resource_type_created(self, resource_type: str) -> bool:
        """Check if any resource of the given type was created."""
        return resource_type in self.created_resources

    def count_resources_of_type(self, resource_type: str) -> int:
        """Count how many resources of the given type were created."""
        return self.created_resources.count(resource_type)


# Global mock instance for easy access
_test_mocks = PulumiTestMocks()


def setup_pulumi_mocks(preview: bool = False) -> PulumiTestMocks:
    """
    Set up Pulumi mocks for testing.

    This is a convenience function that sets up the global mock instance
    and configures Pulumi to use it.

    Args:
        preview: Whether to run in preview mode (default: False)

    Returns:
        The configured mock instance for test inspection
    """
    global _test_mocks
    _test_mocks.reset_tracking()
    pulumi.runtime.set_mocks(_test_mocks, preview=preview)
    return _test_mocks


def get_test_mocks() -> PulumiTestMocks:
    """
    Get the current test mock instance.

    Useful for inspecting what resources were created during tests.
    """
    return _test_mocks


# Helper functions for common test patterns
def assert_resource_created(resource_type: str, expected_count: int = 1):
    """
    Assert that a specific resource type was created the expected number of times.

    Args:
        resource_type: The AWS resource type (e.g., "aws:s3/bucket:Bucket")
        expected_count: Expected number of resources of this type

    Raises:
        AssertionError: If the resource count doesn't match expected
    """
    actual_count = _test_mocks.count_resources_of_type(resource_type)
    if actual_count != expected_count:
        raise AssertionError(
            f"Expected {expected_count} resources of type '{resource_type}', "
            f"but {actual_count} were created. "
            f"Created resources: {_test_mocks.get_created_resources()}"
        )


def assert_resource_not_created(resource_type: str):
    """
    Assert that a specific resource type was NOT created.

    Args:
        resource_type: The AWS resource type that should not exist

    Raises:
        AssertionError: If the resource was created
    """
    if _test_mocks.was_resource_type_created(resource_type):
        raise AssertionError(
            f"Resource type '{resource_type}' should not have been created, "
            f"but it was. Created resources: {_test_mocks.get_created_resources()}"
        )
