# Stretch Goals

This document outlines potential enhancements to the basic infrastructure.

## AWS Systems Manager (SSM) Parameter Store

Add SSM parameters for configuration management and secrets:

```python
import pulumi_aws as aws

# Create SSM parameters
api_config = aws.ssm.Parameter(
    "api-config",
    type="String",
    value='{"version": "1.0", "environment": "dev"}',
    description="API configuration",
    tags={
        "Name": "API Configuration",
        "Environment": "dev",
    },
)

# Create secure string parameter
api_secret = aws.ssm.Parameter(
    "api-secret",
    type="SecureString",
    value="change-me-in-production",
    description="API secret key",
    tags={
        "Name": "API Secret",
        "Environment": "dev",
    },
)

# Update Lambda to read from SSM
# Add IAM policy for SSM access
ssm_policy = aws.iam.RolePolicy(
    "lambda-ssm-policy",
    role=lambda_role.id,
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParametersByPath",
            ],
            "Resource": f"arn:aws:ssm:*:*:parameter/*",
        }],
    }),
)
```

## VPC Configuration

Create a custom VPC with private and public subnets:

```python
import pulumi_aws as aws

# Create VPC
vpc = aws.ec2.Vpc(
    "api-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "API VPC",
        "Environment": "dev",
    },
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway(
    "api-igw",
    vpc_id=vpc.id,
    tags={
        "Name": "API Internet Gateway",
        "Environment": "dev",
    },
)

# Create public subnet
public_subnet = aws.ec2.Subnet(
    "api-public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
    tags={
        "Name": "API Public Subnet",
        "Environment": "dev",
    },
)

# Create private subnet
private_subnet = aws.ec2.Subnet(
    "api-private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-east-1a",
    tags={
        "Name": "API Private Subnet",
        "Environment": "dev",
    },
)

# Create NAT Gateway (requires Elastic IP)
eip = aws.ec2.Eip(
    "api-nat-eip",
    domain="vpc",
    tags={
        "Name": "API NAT Gateway EIP",
        "Environment": "dev",
    },
)

nat_gateway = aws.ec2.NatGateway(
    "api-nat-gateway",
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags={
        "Name": "API NAT Gateway",
        "Environment": "dev",
    },
)

# Create route tables
public_route_table = aws.ec2.RouteTable(
    "api-public-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        ),
    ],
    tags={
        "Name": "API Public Route Table",
        "Environment": "dev",
    },
)

private_route_table = aws.ec2.RouteTable(
    "api-private-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateway.id,
        ),
    ],
    tags={
        "Name": "API Private Route Table",
        "Environment": "dev",
    },
)

# Associate route tables with subnets
public_rt_association = aws.ec2.RouteTableAssociation(
    "api-public-rt-association",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id,
)

private_rt_association = aws.ec2.RouteTableAssociation(
    "api-private-rt-association",
    subnet_id=private_subnet.id,
    route_table_id=private_route_table.id,
)

# Create security group for Lambda
lambda_sg = aws.ec2.SecurityGroup(
    "lambda-sg",
    vpc_id=vpc.id,
    description="Security group for Lambda function",
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": "Lambda Security Group",
        "Environment": "dev",
    },
)

# Update Lambda to use VPC
lambda_function = aws.lambda_.Function(
    "api-lambda",
    role=lambda_role.arn,
    runtime="python3.12",
    handler="index.handler",
    code=...,  # same as before
    vpc_config=aws.lambda_.FunctionVpcConfigArgs(
        subnet_ids=[private_subnet.id],
        security_group_ids=[lambda_sg.id],
    ),
    # ... rest of configuration
)

# Note: Lambda in VPC requires additional IAM permissions
vpc_policy = aws.iam.RolePolicyAttachment(
    "lambda-vpc-policy",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
)
```

## Additional Enhancements

### CloudWatch Logging and Monitoring

```python
# Create CloudWatch Log Group
log_group = aws.cloudwatch.LogGroup(
    "api-logs",
    name=pulumi.Output.concat("/aws/lambda/", lambda_function.name),
    retention_in_days=7,
    tags={
        "Name": "API Logs",
        "Environment": "dev",
    },
)

# Create CloudWatch Alarms
error_alarm = aws.cloudwatch.MetricAlarm(
    "lambda-errors",
    comparison_operator="GreaterThanThreshold",
    evaluation_periods=1,
    metric_name="Errors",
    namespace="AWS/Lambda",
    period=300,
    statistic="Sum",
    threshold=5,
    alarm_description="Lambda function errors",
    dimensions={
        "FunctionName": lambda_function.name,
    },
)
```

### X-Ray Tracing

```python
# Enable X-Ray tracing on Lambda
lambda_function = aws.lambda_.Function(
    "api-lambda",
    # ... other configuration
    tracing_config=aws.lambda_.FunctionTracingConfigArgs(
        mode="Active",
    ),
)

# Add X-Ray permissions to Lambda role
xray_policy = aws.iam.RolePolicyAttachment(
    "lambda-xray-policy",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess",
)
```

### API Gateway Custom Domain

```python
# Certificate (must be in us-east-1 for API Gateway)
certificate = aws.acm.Certificate(
    "api-certificate",
    domain_name="api.example.com",
    validation_method="DNS",
    tags={
        "Name": "API Certificate",
        "Environment": "dev",
    },
)

# Custom domain
domain_name = aws.apigateway.DomainName(
    "api-domain",
    domain_name="api.example.com",
    certificate_arn=certificate.arn,
    tags={
        "Name": "API Custom Domain",
        "Environment": "dev",
    },
)

# Base path mapping
base_path_mapping = aws.apigateway.BasePathMapping(
    "api-mapping",
    rest_api=rest_api.id,
    stage_name=stage.stage_name,
    domain_name=domain_name.domain_name,
)

# Route53 record (if using Route53)
# api_record = aws.route53.Record(
#     "api-record",
#     zone_id="YOUR_ZONE_ID",
#     name="api.example.com",
#     type="A",
#     aliases=[
#         aws.route53.RecordAliasArgs(
#             name=domain_name.cloudfront_domain_name,
#             zone_id=domain_name.cloudfront_zone_id,
#             evaluate_target_health=True,
#         ),
#     ],
# )
```

## Testing Enhancements

### Add Unit Tests

Create `tests/test_infrastructure.py`:

```python
import pytest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + '_id', args.inputs]
    
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# Import your infrastructure
import __main__

@pulumi.runtime.test
def test_bucket_creation():
    def check_bucket(args):
        bucket = args
        assert bucket is not None
    
    return __main__.bucket.id.apply(check_bucket)

@pulumi.runtime.test
def test_dynamodb_table():
    def check_table(args):
        table = args
        assert table is not None
    
    return __main__.dynamodb_table.id.apply(check_table)
```

### Integration Tests

Create a script to test the deployed API:

```python
import requests
import os
import subprocess
import json

def get_api_url():
    result = subprocess.run(
        ["pulumi", "stack", "output", "api_url"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

def test_api_endpoint():
    api_url = get_api_url()
    response = requests.get(api_url)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print(f"✓ API test passed: {data}")

if __name__ == "__main__":
    test_api_endpoint()
```

## Cost Optimization

- Use DynamoDB on-demand pricing initially, switch to provisioned if usage is predictable
- Enable S3 lifecycle policies to transition old objects to cheaper storage classes
- Use API Gateway caching to reduce Lambda invocations
- Set appropriate Lambda memory and timeout values
- Enable CloudWatch Logs retention policies

## Security Enhancements

- Enable S3 bucket encryption
- Enable DynamoDB encryption at rest
- Add API Gateway authentication (Cognito, IAM, or API Keys)
- Implement least privilege IAM policies
- Enable AWS WAF for API Gateway
- Use VPC endpoints for AWS services
- Enable CloudTrail for audit logging
