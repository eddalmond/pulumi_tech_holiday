"""
Shared configuration and utilities for the Pulumi project.

This module provides centralized access to:
- Current stack name
- AWS account information
- AWS region
- Common configuration values
"""

import pulumi
import pulumi_aws as aws


class PulumiConfig:
    """Centralized configuration for Pulumi AWS resources."""

    def __init__(self):
        self._stack_name: str | None = None
        self._current: aws.GetCallerIdentityResult | None = None
        self._region: aws.GetRegionResult | None = None

    def _ensure_initialized(self):
        """Lazy initialization of AWS resources."""
        if self._stack_name is None:
            self._stack_name = pulumi.get_stack()
            self._current = aws.get_caller_identity()
            self._region = aws.get_region()

    @property
    def stack_name(self) -> str:
        """Get the current Pulumi stack name."""
        self._ensure_initialized()
        return self._stack_name

    @property
    def account_id(self) -> str:
        """Get the current AWS account ID."""
        self._ensure_initialized()
        return self._current.account_id

    @property
    def region_name(self) -> str:
        """Get the current AWS region name."""
        self._ensure_initialized()
        return self._region.name

    @property
    def aws_caller_identity(self):
        """Get the AWS caller identity object."""
        self._ensure_initialized()
        return self._current

    @property
    def aws_region(self):
        """Get the AWS region object."""
        self._ensure_initialized()
        return self._region

    def generate_default_tags(
        self, environment: str = None, purpose: str = None
    ) -> dict:
        """Generate standardized tags for AWS resources."""
        self._ensure_initialized()
        tags = {
            "ManagedBy": "Pulumi",
            "Stack": self._stack_name,
            "Region": self._region.name,
        }

        if environment:
            tags["Environment"] = environment
        if purpose:
            tags["Purpose"] = purpose

        return tags


# Global singleton instance
_config = PulumiConfig()
