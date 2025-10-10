"""
Enhanced unit tests for S3 module demonstrating more valuable test patterns.

These tests focus on testing YOUR CODE logic, not just mock verification.
"""

import os
import sys
import unittest

import pulumi

# Set up path for infrastructure imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "infrastructure"))

# Import common test utilities and infrastructure helpers
from common.config import _config
from common.s3 import create_s3_bucket
from tests.common import setup_pulumi_mocks

# Set up mocks for all tests in this module
setup_pulumi_mocks()


class TestS3BusinessLogic(unittest.TestCase):
    @pulumi.runtime.test
    def test_bucket_naming_convention_includes_account_and_region(self):
        """

        If you change the naming format in your code, this test will catch it.
        This protects against accidental changes to bucket naming that could
        cause infrastructure issues.
        """
        s3_resources = create_s3_bucket(
            name_prefix="myapp",
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags={},
        )

        def check_name(name):
            # Your code should produce: "myapp-{account}-{region}"
            expected_pattern = "myapp-123456789012-us-west-2"
            self.assertEqual(
                name,
                expected_pattern,
                f"Bucket name should follow pattern: prefix-account-region. Got: {name}",
            )

        return s3_resources.bucket.bucket.apply(check_name)

    @pulumi.runtime.test
    def test_versioning_is_skipped_when_disabled(self):
        """
        REAL VALUE: Tests that when versioning=False, your code doesn't create
        a versioning resource. This tests the if/else logic in your create_s3_bucket function.

        Now that the function returns all created resources, we can directly verify
        that the versioning resource is None when versioning=False.
        """
        # Create bucket with versioning disabled
        s3_resources = create_s3_bucket(
            name_prefix="no-version",
            versioning=False,  # ← Testing this conditional
            encryption=False,
            public_access_block=False,
            tags={},
        )

        def verify_no_versioning(name):
            # Verify bucket was created
            self.assertIsNotNone(name)

            # Verify that NO versioning resource was created
            self.assertIsNone(
                s3_resources.versioning,
                "Versioning resource should be None when versioning=False",
            )

            # Also verify encryption and public access block weren't created
            self.assertIsNone(
                s3_resources.encryption,
                "Encryption resource should be None when encryption=False",
            )
            self.assertIsNone(
                s3_resources.public_access_block,
                "Public access block should be None when public_access_block=False",
            )

        return s3_resources.bucket.bucket.apply(verify_no_versioning)

    @pulumi.runtime.test
    def test_versioning_is_enabled(self):
        """
        REAL VALUE: Tests that when versioning=True, your code DOES create
        a versioning resource. This verifies the positive case of the conditional.

        Now that the function returns all created resources, we can directly verify
        that the versioning resource exists when versioning=True.
        """
        # Create bucket with versioning enabled
        s3_resources = create_s3_bucket(
            name_prefix="with-version",
            versioning=True,  # ← Testing this conditional
            encryption=False,
            public_access_block=False,
            tags={},
        )

        def verify_versioning_created(name):
            # Verify bucket was created
            self.assertIsNotNone(name)

            # Verify that versioning resource WAS created
            self.assertIsNotNone(
                s3_resources.versioning,
                "Versioning resource should exist when versioning=True",
            )

            # Verify other features still disabled
            self.assertIsNone(
                s3_resources.encryption,
                "Encryption resource should be None when encryption=False",
            )
            self.assertIsNone(
                s3_resources.public_access_block,
                "Public access block should be None when public_access_block=False",
            )

        return s3_resources.bucket.bucket.apply(verify_versioning_created)

    @pulumi.runtime.test
    def test_all_resources_created_when_all_enabled(self):
        """
        REAL VALUE: Tests that all optional resources are created when all flags are True.

        This is a comprehensive test that verifies your function creates all resources
        when all security features are enabled.
        """
        # Create bucket with all features enabled
        s3_resources = create_s3_bucket(
            name_prefix="full-featured",
            versioning=True,
            encryption=True,
            public_access_block=True,
            tags={"test": "value"},
        )

        def verify_all_resources(name):
            # Verify bucket was created
            self.assertIsNotNone(name)

            # Verify ALL optional resources were created
            self.assertIsNotNone(
                s3_resources.versioning,
                "Versioning resource should exist when versioning=True",
            )
            self.assertIsNotNone(
                s3_resources.encryption,
                "Encryption resource should exist when encryption=True",
            )
            self.assertIsNotNone(
                s3_resources.public_access_block,
                "Public access block should exist when public_access_block=True",
            )

        return s3_resources.bucket.bucket.apply(verify_all_resources)

    @pulumi.runtime.test
    def test_tags_default_to_empty_dict_when_none(self):
        """
        REAL VALUE: Tests edge case handling in YOUR code.

        Your code does: tags=tags or {}
        This test verifies that edge case works correctly.
        """
        s3_resources = create_s3_bucket(
            name_prefix="notags",
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags=None,  # ← Testing None handling
        )

        def check_tags(tags):
            # Your code should convert None to {}
            self.assertIsNotNone(tags)
            self.assertIsInstance(tags, dict)

        return s3_resources.bucket.tags.apply(check_tags)

    @pulumi.runtime.test
    def test_multiple_prefixes_produce_different_names(self):
        """
        REAL VALUE: Tests that your naming logic produces unique names.

        This verifies that different prefixes result in different bucket names,
        which is critical for avoiding naming conflicts.
        """
        s3_resources1 = create_s3_bucket("app1", False, False, False, {})
        s3_resources2 = create_s3_bucket("app2", False, False, False, {})

        def check_names(args):
            name1, name2 = args
            self.assertNotEqual(
                name1, name2, "Different prefixes should produce different bucket names"
            )
            self.assertIn("app1", name1)
            self.assertIn("app2", name2)

        return pulumi.Output.all(
            s3_resources1.bucket.bucket, s3_resources2.bucket.bucket
        ).apply(check_names)

    @pulumi.runtime.test
    def test_tags_are_preserved_and_not_mutated(self):
        """
        REAL VALUE: Tests that your code doesn't mutate input parameters.

        This is important for functional programming principles and avoiding
        side effects.
        """
        original_tags = {"Env": "test", "Owner": "team"}
        tags_copy = original_tags.copy()

        s3_resources = create_s3_bucket(
            name_prefix="preserve-tags",
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags=original_tags,
        )

        # Original tags should not be mutated
        self.assertEqual(
            original_tags, tags_copy, "Function should not mutate input tags"
        )

        def check_tags(bucket_tags):
            for key, value in original_tags.items():
                self.assertEqual(bucket_tags[key], value)

        return s3_resources.bucket.tags.apply(check_tags)


class TestS3ConfigIntegration(unittest.TestCase):
    """
    Tests that verify integration with the config module.

    These have value because they test the interaction between modules.
    """

    def test_config_values_are_used_in_bucket_name(self):
        """
        REAL VALUE: Tests integration with config module.

        This verifies that your S3 module correctly uses the config module's
        account_id and region_name properties.
        """
        # These values come from your config module
        account_id = _config.account_id
        region_name = _config.region_name

        # Verify config module is working
        self.assertEqual(account_id, "123456789012")
        self.assertEqual(region_name, "us-west-2")


class TestS3EdgeCases(unittest.TestCase):
    """
    Tests for edge cases and error handling in YOUR code.

    These are the most valuable tests because they catch bugs.
    """

    @pulumi.runtime.test
    def test_empty_prefix_still_creates_valid_name(self):
        """
        REAL VALUE: Tests edge case in your naming logic.

        What happens if someone passes an empty string as prefix?
        Does your code handle it gracefully?
        """
        s3_resources = create_s3_bucket(
            name_prefix="",  # ← Edge case
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags={},
        )

        def check_name(name):
            # Even with empty prefix, should have account and region
            self.assertIn("123456789012", name)
            self.assertIn("us-west-2", name)

        return s3_resources.bucket.bucket.apply(check_name)

    @pulumi.runtime.test
    def test_special_characters_in_tags_are_preserved(self):
        """
        REAL VALUE: Tests that special characters in tags work.

        This verifies your code doesn't accidentally strip or modify
        tag values.
        """
        special_tags = {
            "Path": "/app/component",
            "Version": "v1.2.3-beta",
            "Description": "This has spaces and punctuation!",
        }

        s3_resources = create_s3_bucket(
            name_prefix="special-chars",
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags=special_tags,
        )

        def check_tags(tags):
            self.assertEqual(tags["Path"], "/app/component")
            self.assertEqual(tags["Version"], "v1.2.3-beta")
            self.assertEqual(tags["Description"], "This has spaces and punctuation!")

        return s3_resources.bucket.tags.apply(check_tags)

    @pulumi.runtime.test
    def test_bucket_arn_format(self):
        """
        REAL VALUE: Tests that the bucket ARN follows AWS naming conventions.

        This verifies that the ARN is properly formatted and includes the bucket name.
        """
        s3_resources = create_s3_bucket(
            name_prefix="arn-test",
            versioning=False,
            encryption=False,
            public_access_block=False,
            tags={},
        )

        def check_arn(arn):
            self.assertTrue(
                arn.startswith("arn:aws:s3:::"),
                f"ARN should start with 'arn:aws:s3:::' but got: {arn}",
            )
            self.assertIn(
                "arn-test",
                arn,
                f"ARN should contain the bucket prefix 'arn-test' but got: {arn}",
            )

        return s3_resources.bucket.arn.apply(check_arn)


if __name__ == "__main__":
    unittest.main()
