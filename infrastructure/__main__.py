"""
Unified Pulumi Infrastructure Program

This program deploys different resources based on the stack name:
- 'bootstrap' stack: Creates S3 bucket and DynamoDB table for Pulumi state storage
- Other stacks: Creates the main application infrastructure (API Gateway, Lambda, etc.)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app_layer.app_layer import deploy_application_stack
from bootstrap.bootstrap import deploy_bootstrap_stack

from common.config import _config


def deploy_stack(stack_name: str):
    if stack_name == "bootstrap":
        deploy_bootstrap_stack()
    else:
        deploy_application_stack(stack_name)


# Execute the deployment based on the current stack
deploy_stack(_config.stack_name)
