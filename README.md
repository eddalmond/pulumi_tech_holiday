# pulumi_tech_holiday
Repository to hold assets I create for my Pulumi tech holiday

## Overview

This project uses [Pulumi](https://www.pulumi.com/) to define and manage AWS infrastructure as code using Python. The infrastructure includes a simple API setup with the following AWS services:

- **AWS API Gateway**: REST API endpoint
- **AWS Lambda**: Serverless function to handle API requests
- **AWS S3**: Bucket for storing data/assets
- **AWS DynamoDB**: NoSQL database table

## Prerequisites

- [asdf](https://asdf-vm.com/) version manager for managing multiple runtime versions
- Python 3.13 or later (managed via asdf)
- [Poetry](https://python-poetry.org/) for dependency management (installed via asdf)
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) installed (installed via asdf)
- AWS account with appropriate credentials configured
- AWS CLI configured with valid credentials

## Initial Setup

### 1. Install asdf (if not already installed)

**On macOS:**
```bash
brew install asdf
```

**On Linux:**
```bash
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install required asdf plugins

```bash
# Add Python plugin
asdf plugin add python

# Add Poetry plugin  
asdf plugin add poetry

# Add Pulumi plugin
asdf plugin add pulumi
```

### 3. Install tools using asdf

```bash
# Install Python 3.13 (latest stable)
asdf install python 3.13.1
asdf global python 3.13.1

# Install Poetry
asdf install poetry 1.8.5
asdf global poetry 1.8.5

# Install Pulumi CLI
asdf install pulumi 3.201.0
asdf global pulumi 3.201.0
```

### 4. Verify installations

```bash
python --version    # Should show Python 3.13.1
poetry --version    # Should show Poetry (version 1.8.5)
pulumi version      # Should show v3.201.0
```

## Project Setup

### 1. Install dependencies using Poetry

```bash
poetry install --with dev
```

This will create a virtual environment and install all required dependencies including Pulumi, AWS provider, and the local policy tooling used in CI.

### 2. Configure AWS credentials

Ensure your AWS credentials are configured. You can use:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_REGION=<your-preferred-region>
```

### 3. Bootstrap Infrastructure (One-time setup)

**Create the S3 backend for state storage:**

```bash
# Use local state for bootstrap stack
poetry run pulumi login --local

# Create bootstrap stack to provision S3 bucket and DynamoDB table
poetry run pulumi stack init bootstrap
poetry run pulumi up

# Get the S3 bucket name from outputs
poetry run pulumi stack output state_bucket_name
```

### 4. Switch to S3 Backend

**Configure all future stacks to use S3 backend:**

```bash
# Login to S3 backend (replace with your bucket name from step 3)
poetry run pulumi login s3://pulumi-state-{account-id}-{region}

# Optionally migrate bootstrap stack to S3 backend for consistency
# (See migration section below)
```

### 5. Create Application Stacks

**Initialize application stacks (dev, staging, prod):**

```bash
# Create development stack
poetry run pulumi stack init dev

# Configure AWS region (optional, defaults to your AWS CLI configuration)
poetry run pulumi config set aws:region eu-west-2

# Deploy infrastructure
poetry run pulumi up
```

## Advanced Setup

### Bootstrap Stack Migration (Optional)

For consistency, you can migrate the bootstrap stack from local to S3 backend:

```bash
# 1. Export bootstrap state from local backend
poetry run pulumi login --local
poetry run pulumi stack select bootstrap
poetry run pulumi stack export --file bootstrap-state.json

# 2. Create bootstrap stack in S3 backend
poetry run pulumi login s3://pulumi-state-{account-id}-{region}
poetry run pulumi stack init bootstrap
poetry run pulumi stack import --file bootstrap-state.json

# 3. Clean up
poetry run pulumi login --local
poetry run pulumi stack rm bootstrap --force
rm bootstrap-state.json
```

### Stack Management

**Key concepts:**
- **Bootstrap stack**: Creates S3 bucket and DynamoDB table for state storage
- **Application stacks**: Your actual infrastructure (dev, staging, prod)
- **Conditional deployment**: Same code deploys different resources based on stack name

**Stack workflow:**
```bash
# List all stacks
poetry run pulumi stack ls

# Switch between stacks  
poetry run pulumi stack select {stack-name}

# Check current stack status
poetry run pulumi stack

# View stack outputs
poetry run pulumi stack output
```

## Usage

### Working with Poetry

This project uses Poetry for dependency management and virtual environments. Here are the key commands:

- **Install dependencies**: `poetry install`
- **Activate shell**: `poetry shell`
- **Run commands in venv**: `poetry run <command>`
- **Add new dependency**: `poetry add <package>`
- **Add dev dependency**: `poetry add --group dev <package>`
- **Show dependencies**: `poetry show`
- **Update dependencies**: `poetry update`

### Preview changes with policy packs

To preview what resources will be created and evaluate them against both the AWSGuard (TypeScript) and Python policy packs:

```bash
make policy-preview STACK=dev
```

Alternatively, you can run the underlying command directly:

```bash
poetry run pulumi preview \
	--cwd infrastructure \
	--stack dev \
	--policy-pack ../policies/awsguard \
	--policy-pack-config ../policies/awsguard/policy-config.json \
	--policy-pack ../policies/python
```

### Deploy infrastructure

To create/update the infrastructure:

```bash
poetry run pulumi up
```

### View outputs

After deployment, view the API endpoint and resource names:

```bash
poetry run pulumi stack output
```

### Destroy infrastructure

To tear down all resources:

```bash
poetry run pulumi destroy
```

## Architecture

The infrastructure creates:

1. **S3 Bucket**: For storing data and assets
2. **DynamoDB Table**: With a hash key `id` for storing records
3. **Lambda Function**: Python 3.12 runtime with access to S3 and DynamoDB
4. **API Gateway**: REST API with proxy integration to Lambda
5. **IAM Roles & Policies**: Appropriate permissions for Lambda to access AWS services

## Outputs

After deployment, the following outputs are available:

- `api_url`: The API Gateway endpoint URL
- `bucket_name`: The S3 bucket name
- `dynamodb_table_name`: The DynamoDB table name
- `lambda_function_name`: The Lambda function name

## Testing the API

Once deployed, you can test the API endpoint:

```bash
curl $(poetry run pulumi stack output api_url)
```

The response will include information about the Lambda function and configured resources.

## Extending the Project

### Stretch Goals

The following enhancements can be added:

- **AWS SSM (Systems Manager)**: For parameter store and secrets management
- **VPC Configuration**: Custom VPC with private subnets for Lambda

## Project Structure

```text
.
├── src/
│   └── __main__.py          # Main Pulumi program with conditional deployment logic
├── Pulumi.yaml              # Pulumi project configuration  
├── pyproject.toml           # Poetry dependencies and project config
├── poetry.lock              # Locked dependency versions
├── README.md                # This file
├── .gitignore               # Git ignore patterns
└── requirements.txt         # Legacy Python dependencies (replaced by Poetry)
```

### Code Organization

The project uses a **unified approach** with conditional deployment:

- **Single `__main__.py`**: Contains both bootstrap and application infrastructure code
- **Stack-based routing**: Deploys different resources based on `pulumi.get_stack()` name
- **Bootstrap stack**: Creates S3 bucket and DynamoDB table for state storage
- **Application stacks**: Creates API Gateway, Lambda, S3, DynamoDB for your application

### Dependencies

Managed via **Poetry** with the following key packages:

- `pulumi ^3.201.0`: Core Pulumi SDK
- `pulumi-aws ^7.8.0`: AWS provider for Pulumi
- `python ^3.13`: Python runtime requirement

## License

MIT License - see [LICENSE](LICENSE) file for details
