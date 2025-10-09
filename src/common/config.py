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

# These will be initialized when first accessed
_stack_name = None
_current = None
_region = None

def _ensure_initialized():
    """Lazy initialization of AWS resources."""
    global _stack_name, _current, _region
    if _stack_name is None:
        _stack_name = pulumi.get_stack()
        _current = aws.get_caller_identity()
        _region = aws.get_region()

def get_stack_name() -> str:
    """Get the current Pulumi stack name."""
    _ensure_initialized()
    return _stack_name

def get_account_id() -> str:
    """Get the current AWS account ID."""
    _ensure_initialized()
    return _current.account_id

def get_region_name() -> str:
    """Get the current AWS region name."""
    _ensure_initialized()
    return _region.name

def get_aws_caller_identity():
    """Get the AWS caller identity object."""
    _ensure_initialized()
    return _current

def get_aws_region():
    """Get the AWS region object."""
    _ensure_initialized()
    return _region

# Common tag patterns
def get_default_tags(environment: str = None, purpose: str = None) -> dict:
    """Generate standardized tags for AWS resources."""
    _ensure_initialized()
    tags = {
        "ManagedBy": "Pulumi",
        "Stack": _stack_name,
        "Region": _region.name,
    }
    
    if environment:
        tags["Environment"] = environment
    if purpose:
        tags["Purpose"] = purpose
        
    return tags