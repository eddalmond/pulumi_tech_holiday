# CI/CD Pipeline Documentation

This project ships with a GitHub Actions workflow that validates infrastructure code, enforces security guardrails, and keeps the Python codebase healthy.

## Pipeline Overview

The GitHub Actions workflow (`.github/workflows/ci.yml`) is triggered on every pull request event (`opened`, `synchronize`, `reopened`). It runs four coordinated jobs:

### 1. Code Quality & Security Scans (`lint-and-format`)

- **Ruff**: Linting (`ruff check`) and format enforcement (`ruff format --check`)
- **Black**: Formatting parity check (`black --check --diff`)
- **MyPy**: Static type checking over `infrastructure/` and `src/`
- **Bandit**: Python security linting (JSON artifact + console output)
- **Safety**: Dependency vulnerability scanning (JSON artifact + console output)
- **Poetry Cache**: Reuses the `.venv` directory when the `poetry.lock` hash is unchanged

### 2. Policy-Driven Infrastructure Preview (`pulumi-security-checks`)

- Installs the Pulumi CLI and logs into an ephemeral file-backed backend
- Ensures the `dev` stack exists before previewing
- Runs `pulumi preview` against `infrastructure/` with both the AWSGuard (TypeScript) and bespoke Python policy packs
- Compiles the Python policy pack to surface syntax issues quickly
- Requires AWS credentials and a Pulumi config passphrase via repository secrets

### 3. Unit Tests & Coverage (`unit-tests`)

- Executes the `pytest` suite under Poetry
- Produces terminal, XML, and HTML coverage reports for `infrastructure/` and `src/`
- Publishes JUnit XML, HTML test report, and the `htmlcov/` directory as artifacts

### 4. Build Summary (`summary`)

- Aggregates status from preceding jobs
- Fails the workflow with a helpful message if any dependency job fails

## Running Locally

Use the provided `Makefile` to mirror the CI workflow locally (Make targets wrap Poetry commands and optional extras such as Checkov):

```bash
# Install all dependencies
make install

# Format code
make format

# Run linting checks
make lint

# Run security checks (Bandit, Safety, Checkov)
make security

# Run unit tests
make test

# Run full CI pipeline locally (lint → security → tests)
make ci

# Format + lint combo before committing
make pre-commit
```

## Configuration Files

- `pyproject.toml`: Poetry project configuration plus tool settings for Ruff, Black, MyPy, pytest, coverage, Bandit, and Safety
- `ruff.toml`: Ruff rules and formatter preferences
- `Makefile`: One-stop entry point for local formatting, linting, testing, security scans, and Pulumi preview
- `policies/awsguard/policy-config.json`: Configuration for the AWSGuard policy pack executed during `pulumi preview`
- `policies/python/policy-config.json`: Settings for the custom Python policy pack

## CI/CD Triggers

The workflow currently runs on pull request events only (`opened`, `synchronize`, `reopened`).
Add additional triggers (for example branch pushes or scheduled runs) by editing the `on:` block in `.github/workflows/ci.yml`.

## Required Secrets

The policy preview job needs these repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `PULUMI_CONFIG_PASSPHRASE` (can be empty but must be present)

Because the workflow uses a local file-backed backend for Pulumi previews, a `PULUMI_ACCESS_TOKEN` is not required.

## Workflow Jobs

### lint-and-format (Code Quality & Linting)

- Installs Poetry and project dependencies (cached virtualenv when possible)
- Runs Ruff lint/format checks, Black, MyPy, Bandit, and Safety
- Uploads Bandit and Safety JSON reports as `security-reports`

### pulumi-security-checks (Infrastructure Policy Preview)

- Installs Poetry, Pulumi CLI, Node.js, and policy-pack dependencies
- Compiles the Python policy pack to detect syntax issues
- Runs `pulumi preview` with both policy packs to gate infrastructure changes

### unit-tests (Test Suite & Coverage)

- Executes `pytest` with coverage for `infrastructure/` and `src/`
- Emits HTML + XML reports and uploads them as `test-results`

### summary (Build Summary)

- Prints individual job outcomes
- Fails fast if any prerequisite job fails

## Artifacts

The workflow exposes these downloadable artifacts on each run:

- **security-reports**: `bandit-report.json`, `safety-report.json`
- **test-results**: `pytest-results.xml`, `pytest-report.html`, `htmlcov/`

## Customization

### Skip or Tune Specific Checks

- `ruff.toml`: Add rule codes to `ignore` or `extend-select`
- `pyproject.toml`: Update configuration blocks for MyPy, Bandit, Safety, pytest, and coverage
- `Makefile`: Remove or adjust commands for local workflows (for example disable Checkov if not needed)

### Add More Automation

1. Extend `.github/workflows/ci.yml` with extra steps or jobs
2. Add matching Make targets so contributors can replicate changes locally
3. Capture additional artifacts with `actions/upload-artifact`

### Environment-Specific Extensions

- Add a deployment job that depends on `summary`
- Parameterize stack names, policy packs, or AWS regions through workflow inputs or repository variables

## Troubleshooting

### Common Issues

1. **MyPy import errors**: Update `pyproject.toml` under `[tool.mypy]` or use the `--ignore-missing-imports` flag locally
2. **Ruff violations**: Run `make format` to apply Ruff + Black or tailor ignore lists in `ruff.toml`
3. **Bandit/Safety findings**: Review the JSON artifacts for context, then suppress intentionally via `pyproject.toml` or upgrade dependencies
4. **Pulumi preview failures**: Re-run `make policy-preview STACK=dev` locally to reproduce and iterate
5. **Test failures**: Execute `make test` for detailed pytest output and coverage reports

### Getting Help

- Check the workflow logs in GitHub Actions
- Run individual tools locally using the Makefile
- Review tool documentation for specific configuration options

