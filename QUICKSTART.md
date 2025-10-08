# Quick Start Guide

This guide will help you get started with deploying your Pulumi infrastructure in 5 minutes.

## Prerequisites Check

Before you begin, verify you have:

```bash
# Check Pulumi is installed
pulumi version

# Check Python is installed (3.7+)
python3 --version

# Check AWS CLI is configured
aws sts get-caller-identity
```

## Setup Steps

### 1. Clone and Install Dependencies

```bash
# Navigate to the project directory
cd pulumi_tech_holiday

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Login to Pulumi Backend

Choose one of the following:

**Option A: Local State (No account needed)**
```bash
export PULUMI_CONFIG_PASSPHRASE=""
pulumi login --local
```

**Option B: Pulumi Cloud (Free account)**
```bash
pulumi login
```

### 3. Initialize the Stack

```bash
# If you haven't already created the stack
pulumi stack init dev

# Set AWS region (optional, uses your AWS CLI default)
pulumi config set aws:region us-east-1
```

### 4. Preview Infrastructure

See what will be created without actually creating it:

```bash
pulumi preview
```

This will show you:
- 1 S3 Bucket
- 1 DynamoDB Table
- 1 Lambda Function
- 1 API Gateway REST API
- IAM Roles and Policies
- Total: ~15-20 resources

### 5. Deploy Infrastructure

```bash
pulumi up
```

Type "yes" when prompted to create the resources.

⏱️ Deployment typically takes 2-3 minutes.

### 6. Test Your API

Once deployed, get your API endpoint:

```bash
pulumi stack output api_url
```

Test it with curl:

```bash
curl $(pulumi stack output api_url)
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
pulumi stack output
```

You'll see:
- `api_url`: Your API Gateway endpoint
- `bucket_name`: S3 bucket name
- `dynamodb_table_name`: DynamoDB table name
- `lambda_function_name`: Lambda function name

### Modify the Lambda Function

Edit the Lambda code in `__main__.py` (look for the `pulumi.StringAsset` section):

```python
code=pulumi.AssetArchive({
    "index.py": pulumi.StringAsset("""
# Your Lambda code here
"""),
}),
```

Then redeploy:
```bash
pulumi up
```

### Update Infrastructure

Make changes to `__main__.py` and run:

```bash
pulumi up
```

Pulumi will show you what will change and ask for confirmation.

### Clean Up

When you're done, destroy all resources:

```bash
pulumi destroy
```

Type "yes" to confirm. This removes all AWS resources.

## Common Commands

```bash
# View current stack
pulumi stack

# View resource details
pulumi stack export

# View logs from last deployment
pulumi logs --follow

# Get specific output value
pulumi stack output api_url

# List all stacks
pulumi stack ls

# Switch stacks
pulumi stack select <stack-name>

# View config
pulumi config

# Set config value
pulumi config set <key> <value>

# Set secret config value (encrypted)
pulumi config set --secret <key> <value>
```

## Troubleshooting

### Issue: "No credentials found"

```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

### Issue: "Stack already exists"

```bash
# Select the existing stack
pulumi stack select dev
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
pulumi plugin install resource aws v6.83.0
```

## Cost Estimate

With this basic setup:
- **S3**: ~$0.023 per GB stored + requests
- **DynamoDB**: Pay-per-request (free tier: 25 GB storage)
- **Lambda**: Free tier: 1M requests/month + 400,000 GB-seconds
- **API Gateway**: Free tier: 1M requests/month
- **Estimated monthly cost**: **$0-5** for development/testing

💡 Remember to run `pulumi destroy` when not using the infrastructure to avoid charges.

## Learn More

- [Pulumi AWS Documentation](https://www.pulumi.com/registry/packages/aws/)
- [Pulumi Python Guide](https://www.pulumi.com/docs/languages-sdks/python/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Stretch Goals](STRETCH_GOALS.md) - Add VPC, SSM, and more
