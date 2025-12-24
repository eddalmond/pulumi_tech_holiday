import pulumi
import pulumi_aws as aws

from common.apigateway import LambdaRestApi


def create_lambda_rest_api(
    name: str,
    lambda_function: aws.lambda_.Function,
    stage_name: str,
    description: str | None = None,
    enable_proxy_route: bool = True,
    enable_root_route: bool = True,
    tags: dict[str, str] | None = None,
) -> tuple[LambdaRestApi, aws.apigateway.Stage, pulumi.Output[str]]:
    """
    Create a REST API Gateway with Lambda integration using sensible defaults.

    This is a convenience function that creates an API with common patterns:
    - Root route (/) with ANY method
    - Proxy route ({proxy+}) with ANY method for catch-all
    - Automatic deployment to the specified stage

    Args:
        name: Base name for the API resources
        lambda_function: The Lambda function to integrate with
        stage_name: The deployment stage name
        description: Optional description for the API
        enable_proxy_route: Enable catch-all proxy route (default: True)
        enable_root_route: Enable root route (default: True)
        tags: Optional tags to apply to resources

    Returns:
        Tuple of (LambdaRestApi instance, Stage, endpoint URL)
    """
    # Create the API
    api = LambdaRestApi(
        name=name,
        lambda_function=lambda_function,
        stage_name=stage_name,
        description=description,
        tags=tags,
    )

    # Add root route if enabled
    if enable_root_route:
        api.add_root_route(methods=["ANY"])

    # Add proxy route if enabled
    if enable_proxy_route:
        api.add_proxy_route(path="{proxy+}", methods=["ANY"])

    # Deploy the API
    stage = api.deploy()

    # Get the endpoint URL
    endpoint_url = api.get_endpoint_url(stage)

    return api, stage, endpoint_url
