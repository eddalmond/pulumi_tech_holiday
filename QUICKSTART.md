# Quick Start Guide

This guide shows how to deploy the Pulumi reference stack in about five minutes.

## Prerequisites Check

Before you begin, confirm you have:

```bash
# Check Pulumi is installed
pulumi version

# Check Python is installed (3.13+)
python --version

# Check AWS CLI is configured
aws sts get-caller-identity
```

## Setup Steps

### 1. Clone and Install Dependencies

```bash
# Navigate to the project directory
cd pulumi_tech_holiday

# Install dependencies and create the virtual environment
poetry install --with dev

# (Optional) Activate the Poetry shell for shorter commands
poetry shell
```

### 2. Login to Pulumi Backend

Choose one of the following:

#### Option A: Local State (no account needed)

```bash
export PULUMI_CONFIG_PASSPHRASE=""
poetry run pulumi login --local
```

#### Option B: Pulumi Cloud (free account)

```bash
poetry run pulumi login
```

### 3. Initialize the Stack

```bash
# If you haven't already created the stack
poetry run pulumi stack init dev

# Set AWS region (optional, uses your AWS CLI default)
poetry run pulumi config set aws:region eu-west-2
```

### 4. Preview Infrastructure

See what will be created without actually provisioning resources:

```bash
poetry run pulumi preview --cwd infrastructure --stack dev
```

This will show you:

- 1 S3 bucket
- 1 DynamoDB table
- 1 Lambda function
- 1 API Gateway REST API
- IAM roles and policies
- Total: ~15-20 resources

### 5. Deploy Infrastructure

```bash
poetry run pulumi up --cwd infrastructure --stack dev
```

Type "yes" when prompted to create the resources.

⏱️ Deployment typically takes 2-3 minutes.

### 6. Test Your API

Once deployed, get your API endpoint:

```bash
poetry run pulumi stack output api_url
```

Test it with curl:

```bash
curl $(poetry run pulumi stack output api_url)
```

Expected response:

```json
{
  "message": "Hello from Pulumi Lambda!",
  "path": "/",
  "method": "GET",
  "dynamodb_table": "api-table-xxx",
  "s3_bucket": "api-bucket-xxx"
}
```

## Next Steps

### View All Outputs

```bash
poetry run pulumi stack output
```

You'll see:

- `api_url`: API Gateway endpoint
- `bucket_name`: S3 bucket name
- `dynamodb_table_name`: DynamoDB table name
- `lambda_function_name`: Lambda function name

### Modify the Lambda Function

Edit the handler in `src/lambda/app.py`, then redeploy:

```bash
poetry run pulumi up --cwd infrastructure --stack dev
```

### Update Infrastructure

Adjust the Pulumi program under `infrastructure/` (for example `app_layer/app_layer.py`) and redeploy:

```bash
poetry run pulumi up --cwd infrastructure --stack dev
```

Pulumi will show you the proposed changes and ask for confirmation before applying them.

### Clean Up

When you're done, destroy all resources:

```bash
poetry run pulumi destroy --cwd infrastructure --stack dev
```

Type "yes" to confirm. This removes all AWS resources.

## Common Commands

```bash
# View current stack
poetry run pulumi stack

# View resource details
poetry run pulumi stack export

# View logs from last deployment
poetry run pulumi logs --follow

# Get a specific output value
poetry run pulumi stack output api_url

# List all stacks
poetry run pulumi stack ls

# Switch stacks
poetry run pulumi stack select <stack-name>

# View config values
poetry run pulumi config

# Set config value
poetry run pulumi config set <key> <value>

# Set secret config value (encrypted)
poetry run pulumi config set --secret <key> <value>
```

## Troubleshooting

### Issue: "No credentials found"

```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=eu-west-2
```

### Issue: "Stack already exists"

```bash
# Select the existing stack
poetry run pulumi stack select dev
```

### Issue: "passphrase must be set"

```bash
# Set an empty passphrase for local development
export PULUMI_CONFIG_PASSPHRASE=""
```

### Issue: Plugin download fails

If you're behind a firewall or have network issues:

```bash
# Manually install the AWS plugin
poetry run pulumi plugin install resource aws v6.83.0
```

## Cost Estimate

With this basic setup:

- **S3**: ~$0.023 per GB stored + requests
- **DynamoDB**: Pay-per-request (free tier: 25 GB storage)
- **Lambda**: Free tier: 1M requests/month + 400,000 GB-seconds
- **API Gateway**: Free tier: 1M requests/month
- **Estimated monthly cost**: **$0-5** for development/testing

💡 Remember to run `pulumi destroy` when you're not using the infrastructure to avoid charges.

## Learn More

- [Pulumi AWS Documentation](https://www.pulumi.com/registry/packages/aws/)
- [Pulumi Python Guide](https://www.pulumi.com/docs/languages-sdks/python/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Stretch Goals](STRETCH_GOALS.md) — add VPC, SSM, and more
