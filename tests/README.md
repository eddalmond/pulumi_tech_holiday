# Pulumi Infrastructure Testing

This directory contains unit tests for the Pulumi infrastructure code.

## Running Tests

### Prerequisites

Install test dependencies:
```bash
poetry add --group dev pytest pulumi
```

### Run All Tests

```bash
# Using Poetry
poetry run pytest tests/

# Or with Python directly
poetry run python -m pytest tests/

# Run with verbose output
poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/test_s3.py -v
```

### Run Specific Tests

```bash
# Run a specific test class
poetry run pytest tests/test_s3.py::TestS3BucketCreation -v

# Run a specific test method
poetry run pytest tests/test_s3.py::TestS3BucketCreation::test_bucket_created_with_correct_name -v
```

## Test Structure

### Mocking

Tests use Pulumi's `pulumi.runtime.Mocks` class to mock:
1. **Resource Creation** (`new_resource`): Returns mock resource IDs and state
2. **Provider Calls** (`call`): Returns mock data for AWS API calls like `get_caller_identity()`

Example mock setup:
```python
class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args):
        # Return [id, state_dict]
        return [f"{args.name}-id", args.inputs]
    
    def call(self, args):
        # Return mock data for provider calls
        if args.token == "aws:index/getCallerIdentity:getCallerIdentity":
            return {"accountId": "123456789012"}
        return {}

pulumi.runtime.set_mocks(MyMocks(), preview=False)
```

### Test Patterns

#### Testing Output Values

Since Pulumi properties are `Output` objects (resolved asynchronously), use `.apply()`:

```python
@pulumi.runtime.test
def test_bucket_name(self):
    bucket = create_s3_bucket(...)
    
    def check_name(name):
        self.assertIn("expected-value", name)
    
    return bucket.bucket.apply(check_name)
```

#### Testing Multiple Outputs

Use `pulumi.Output.all()` to test multiple properties:

```python
@pulumi.runtime.test
def test_multiple_properties(self):
    bucket = create_s3_bucket(...)
    
    def check_properties(args):
        name, tags, arn = args
        self.assertIsNotNone(name)
        self.assertEqual(tags["Environment"], "test")
        self.assertTrue(arn.startswith("arn:aws:s3:::"))
    
    return pulumi.Output.all(
        bucket.bucket,
        bucket.tags,
        bucket.arn
    ).apply(check_properties)
```

## Test Coverage

Current test files:
- `test_s3.py`: Tests for S3 bucket creation functions
  - Bucket naming conventions
  - Tag application
  - Versioning configuration
  - Encryption configuration
  - Public access blocking
  - ARN format validation

## Writing New Tests

### 1. Create Test File

Create a new file in `tests/` directory:
```python
# tests/test_mymodule.py
import unittest
import pulumi
from common.mymodule import my_function

class TestMyModule(unittest.TestCase):
    @pulumi.runtime.test
    def test_something(self):
        # Your test here
        pass
```

### 2. Set Up Mocks

Define mocks for any resources or provider calls your code uses.

### 3. Write Test Cases

Use the `@pulumi.runtime.test` decorator for async tests.

### 4. Run Tests

```bash
poetry run pytest tests/test_mymodule.py -v
```

## Resources

- [Pulumi Testing Documentation](https://www.pulumi.com/docs/iac/concepts/testing/unit/)
- [Pulumi Testing Examples](https://github.com/pulumi/examples/tree/master/testing-unit-py)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
