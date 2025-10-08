# pulumi_tech_holiday
Repository to hold assets I create for my Pulumi tech holiday

## Overview

This project uses [Pulumi](https://www.pulumi.com/) to define and manage AWS infrastructure as code using Python. The infrastructure includes a simple API setup with the following AWS services:

- **AWS API Gateway**: REST API endpoint
- **AWS Lambda**: Serverless function to handle API requests
- **AWS S3**: Bucket for storing data/assets
- **AWS DynamoDB**: NoSQL database table

## Prerequisites

- Python 3.9 or later
- [Poetry](https://python-poetry.org/) for dependency management
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) installed
- AWS account with appropriate credentials configured
- AWS CLI configured with valid credentials

## Setup

1. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

   This will create a virtual environment and install all required dependencies including Pulumi and AWS provider.

2. **Activate the Poetry virtual environment**:
   ```bash
   poetry shell
   ```
   
   Or run commands within the virtual environment using:
   ```bash
   poetry run <command>
   ```

2. **Configure AWS credentials**:
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

3. **Login to Pulumi**:

   ```bash
   # For local state storage
   poetry run pulumi login --local
   
   # Or for Pulumi Cloud
   poetry run pulumi login
   ```

4. **Initialize the stack**:

   ```bash
   poetry run pulumi stack init dev
   ```

5. **Configure the AWS region** (optional, defaults to your AWS CLI configuration):

   ```bash
   poetry run pulumi config set aws:region eu-west-2
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

### Preview changes

To preview what resources will be created:

```bash
poetry run pulumi preview
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

```
.
├── __main__.py           # Main Pulumi program defining infrastructure
├── Pulumi.yaml          # Pulumi project configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore patterns
```

## License

MIT License - see [LICENSE](LICENSE) file for details
