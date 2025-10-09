# CI/CD Pipeline Documentation

This project includes a comprehensive CI/CD pipeline that ensures code quality, security, and reliability.

## Pipeline Overview

The GitHub Actions workflow (`.github/workflows/ci.yml`) includes three main stages:

### 1. Code Quality & Linting
- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatting
- **isort**: Import sorting
- **MyPy**: Static type checking
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability scanning

### 2. Infrastructure Security & Compliance
- **Checkov**: Infrastructure as Code security scanning
- **TFSEC**: Terraform security analysis (for converted Pulumi code)
- **Terrascan**: Multi-cloud security scanning
- **Pulumi Policy as Code**: Custom policy validation

### 3. Unit Tests
- **pytest**: Unit test execution
- **Coverage**: Code coverage reporting
- **HTML Reports**: Detailed test and coverage reports

## Running Locally

Use the provided Makefile to run the same checks locally:

```bash
# Install all dependencies
make install

# Format code
make format

# Run linting checks
make lint

# Run security checks
make security

# Run unit tests
make test

# Run full CI pipeline locally
make ci

# Quick pre-commit check
make pre-commit
```

## Configuration Files

- `ruff.toml`: Ruff linter configuration
- `pyproject.toml`: Python project configuration (includes mypy, black, isort, pytest, coverage, bandit)
- `.checkov.yml`: Checkov security scanner configuration

## CI/CD Triggers

The pipeline runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Required Secrets

For full functionality, configure these GitHub repository secrets:

- `AWS_ACCESS_KEY_ID`: AWS access key for infrastructure validation
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for infrastructure validation  
- `PULUMI_ACCESS_TOKEN`: Pulumi Cloud access token for state management

## Workflow Jobs

### lint-and-format
- Installs Python dependencies
- Runs code quality tools
- Uploads security reports as artifacts

### pulumi-security-checks  
- Runs infrastructure security scanning
- Generates compliance reports
- Uploads scan results as artifacts

### unit-tests
- Executes test suite with coverage
- Generates test reports
- Uploads test artifacts
- Optional Codecov integration

### integration-check
- Validates infrastructure changes
- Runs Pulumi preview (dry-run)
- Only runs on pull requests

### summary
- Aggregates results from all jobs
- Provides overall pass/fail status

## Artifacts

The pipeline generates several artifacts:

- **Security Reports**: Bandit and Safety scan results
- **Checkov Reports**: Infrastructure security findings  
- **Test Results**: JUnit XML and HTML test reports
- **Coverage Reports**: HTML coverage reports

## Customization

### Skip Certain Checks

Edit the configuration files to skip specific checks:

- `ruff.toml`: Add check codes to `ignore` list
- `.checkov.yml`: Add check IDs to `skip-check` list  
- `pyproject.toml`: Modify tool-specific configurations

### Add More Tools

Extend the workflow by adding more security or quality tools:

1. Add installation commands to the workflow
2. Add execution steps
3. Update the Makefile for local development

### Environment-Specific Configuration

The workflow supports different environments:
- Development: Full validation and preview
- Production: Additional deployment steps (can be added)

## Troubleshooting

### Common Issues

1. **MyPy Import Errors**: Add problematic modules to the `ignore_missing_imports` list
2. **Ruff Violations**: Fix automatically with `make format` or configure exceptions
3. **Checkov False Positives**: Add specific check IDs to the skip list
4. **Test Failures**: Run `make test` locally for detailed debugging

### Getting Help

- Check the workflow logs in GitHub Actions
- Run individual tools locally using the Makefile
- Review tool documentation for specific configuration options