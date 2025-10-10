# Makefile for local development and CI/CD commands
.PHONY: help install lint format test security clean ci

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  lint           - Run all linting checks"
	@echo "  format         - Format code automatically"
	@echo "  test           - Run unit tests with coverage"
	@echo "  security       - Run security checks (Bandit, Safety, Checkov)"
	@echo "  policy-preview - Run pulumi preview with policy packs"
	@echo "  clean          - Clean up temporary files"
	@echo "  ci             - Run full CI pipeline locally"

# Install dependencies
install:
	poetry install --with dev
	pip install checkov

# Format code automatically
format:
	poetry run ruff format .
	poetry run black .
	poetry run isort .

# Run linting checks
lint:
	@echo "Running Ruff linting..."
	poetry run ruff check .
	@echo "Running Ruff format check..."
	poetry run ruff format --check .
	@echo "Running Black format check..."
	poetry run black --check --diff .
	@echo "Running isort check..."
	poetry run isort --check-only --diff .
	@echo "Running MyPy type checking..."
	poetry run mypy infrastructure/ src/ --ignore-missing-imports

# Run security checks
security:
	@echo "Running Bandit security linting..."
	poetry run bandit -r infrastructure/ src/
	@echo "Running Safety dependency check..."
	poetry run safety check
	@echo "Running Checkov infrastructure security check..."
	checkov -d infrastructure/ --framework pulumi --framework python

STACK ?= dev

policy-preview:
	mkdir -p .pulumi
	poetry run pulumi login --cloud-url "file://$(PWD)/.pulumi"
	poetry run pulumi stack select $(STACK) --cwd infrastructure --non-interactive || \
		poetry run pulumi stack init $(STACK) --cwd infrastructure
	poetry run pulumi preview \
		--stack $(STACK) \
		--cwd infrastructure \
		--non-interactive \
		--policy-pack ../policies/awsguard \
		--policy-pack-config ../policies/awsguard/policy-config.json \
		--policy-pack ../policies/python \
		--policy-pack-config ../policies/python/policy-config.json

# Run unit tests with coverage
test:
	poetry run pytest tests/ \
		--cov=infrastructure \
		--cov=src \
		--cov-report=xml \
		--cov-report=html \
		--cov-report=term \
		--junit-xml=pytest-results.xml \
		--html=pytest-report.html \
		--self-contained-html \
		-v

# Clean up temporary files
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf pytest-results.xml
	rm -rf pytest-report.html
	rm -rf bandit-report.json
	rm -rf safety-report.json
	rm -rf results_*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run full CI pipeline locally
ci: lint security test
	@echo "✅ All CI checks completed successfully!"

# Quick check before committing
pre-commit: format lint
	@echo "✅ Code formatted and linted successfully!"