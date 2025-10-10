"""
API Gateway helper classes and functions for creating REST APIs with Lambda integrations.

This module provides a clean abstraction for creating API Gateway REST APIs
with Lambda proxy integrations, supporting multiple routes and methods.
"""

import pulumi
import pulumi_aws as aws
from common.config import _config


class LambdaRestApi:
    """
    A REST API Gateway with Lambda proxy integration.

    This class manages the creation of an API Gateway REST API, routes,
    methods, Lambda integrations, and deployments.
    """

    def __init__(
        self,
        name: str,
        lambda_function: aws.lambda_.Function,
        stage_name: str,
        description: str | None = None,
        tags: dict[str, str] | None = None,
    ):
        """
        Initialize a new Lambda REST API.

        Args:
            name: Base name for the API resources
            lambda_function: The Lambda function to integrate with
            stage_name: The deployment stage name (e.g., 'dev', 'prod')
            description: Optional description for the API
            tags: Optional tags to apply to resources
        """
        self.name = name
        self.lambda_function = lambda_function
        self.stage_name = stage_name
        self.tags = tags or {}

        # Create the REST API
        self.rest_api = aws.apigateway.RestApi(
            f"{name}-api", description=description or f"{name} REST API", tags=self.tags
        )

        # Track all integrations for deployment dependencies
        self._integrations: list[aws.apigateway.Integration] = []

        # Grant API Gateway permission to invoke Lambda
        self.lambda_permission = aws.lambda_.Permission(
            f"{name}-api-lambda-permission",
            action="lambda:InvokeFunction",
            function=lambda_function.name,
            principal="apigateway.amazonaws.com",
            source_arn=pulumi.Output.concat(self.rest_api.execution_arn, "/*/*"),
        )

    def add_proxy_route(
        self,
        path: str = "{proxy+}",
        methods: list[str] = None,
        authorization: str = "NONE",
    ) -> None:
        """
        Add a proxy route that captures all sub-paths.

        Args:
            path: The path pattern (default: "{proxy+}" for catch-all)
            methods: List of HTTP methods (default: ["ANY"])
            authorization: Authorization type (default: "NONE")
        """
        if methods is None:
            methods = ["ANY"]

        # Create resource for the path
        resource = aws.apigateway.Resource(
            f"{self.name}-resource-{path.replace('{', '').replace('}', '').replace('+', 'plus')}",
            rest_api=self.rest_api.id,
            parent_id=self.rest_api.root_resource_id,
            path_part=path,
        )

        # Add methods for this resource
        for method in methods:
            self._add_method_with_lambda_integration(
                resource_id=resource.id,
                http_method=method,
                authorization=authorization,
                resource_name=path,
            )

    def add_root_route(
        self, methods: list[str] = None, authorization: str = "NONE"
    ) -> None:
        """
        Add methods to the root resource (/).

        Args:
            methods: List of HTTP methods (default: ["ANY"])
            authorization: Authorization type (default: "NONE")
        """
        if methods is None:
            methods = ["ANY"]

        for method in methods:
            self._add_method_with_lambda_integration(
                resource_id=self.rest_api.root_resource_id,
                http_method=method,
                authorization=authorization,
                resource_name="root",
            )

    def _add_method_with_lambda_integration(
        self,
        resource_id: pulumi.Output[str],
        http_method: str,
        authorization: str,
        resource_name: str,
    ) -> None:
        """
        Add a method with Lambda proxy integration.

        Args:
            resource_id: The API Gateway resource ID
            http_method: The HTTP method (GET, POST, ANY, etc.)
            authorization: Authorization type
            resource_name: Name for the resource (for naming)
        """
        method_name = f"{self.name}-{resource_name}-{http_method.lower()}-method"

        # Create the method
        method = aws.apigateway.Method(
            method_name,
            rest_api=self.rest_api.id,
            resource_id=resource_id,
            http_method=http_method,
            authorization=authorization,
        )

        # Create Lambda proxy integration
        integration = aws.apigateway.Integration(
            f"{method_name}-integration",
            rest_api=self.rest_api.id,
            resource_id=resource_id,
            http_method=method.http_method,
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=self.lambda_function.invoke_arn,
        )

        self._integrations.append(integration)

    def deploy(self) -> aws.apigateway.Stage:
        """
        Deploy the API to a stage.

        Returns:
            The created API Gateway stage
        """
        # Create deployment (depends on all integrations)
        deployment = aws.apigateway.Deployment(
            f"{self.name}-deployment",
            rest_api=self.rest_api.id,
            opts=pulumi.ResourceOptions(depends_on=self._integrations),
        )

        # Create stage
        stage = aws.apigateway.Stage(
            f"{self.name}-stage",
            rest_api=self.rest_api.id,
            deployment=deployment.id,
            stage_name=self.stage_name,
            tags={**self.tags, "Name": f"{self.stage_name.title()} Stage"},
        )

        return stage

    def get_endpoint_url(self, stage: aws.apigateway.Stage) -> pulumi.Output[str]:
        """
        Get the full endpoint URL for the API.

        Args:
            stage: The API Gateway stage

        Returns:
            The full HTTPS endpoint URL
        """
        return pulumi.Output.concat(
            "https://",
            self.rest_api.id,
            ".execute-api.",
            _config.region_name,
            ".amazonaws.com/",
            stage.stage_name,
            "/",
        )
