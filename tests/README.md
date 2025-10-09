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

Tests use a centralized mocking system from `tests/common.py` that provides:

1. **Resource Creation** (`new_resource`): Returns realistic mock resource IDs and state for all AWS resource types
2. **Provider Calls** (`call`): Returns mock data for AWS API calls like `get_caller_identity()`
3. **Resource Tracking**: Tracks what resources are created for test verification
4. **Helper Functions**: Convenience functions for common test assertions

#### Using Common Mocks

The easiest way to set up mocks for any test file:

```python
import unittest
import pulumi
from tests.common import setup_pulumi_mocks

# Set up mocks for all tests in this module
setup_pulumi_mocks()

class TestMyInfrastructure(unittest.TestCase):
    @pulumi.runtime.test
    def test_something(self):
        # Your test here - mocks are automatically configured
        pass
```

#### Advanced Mock Usage

For more control over mocking:

```python
from tests.common import PulumiTestMocks, get_test_mocks, assert_resource_created

# Custom mock instance
mocks = PulumiTestMocks()
pulumi.runtime.set_mocks(mocks, preview=False)

# Access global mock instance
test_mocks = get_test_mocks()

# Check what resources were created
assert_resource_created("aws:s3/bucket:Bucket", expected_count=1)
assert_resource_not_created("aws:s3/bucketVersioning:BucketVersioning")

# Inspect created resources
created_resources = test_mocks.get_created_resources()
resource_output = test_mocks.get_resource_output("my-bucket")
```

#### Supported AWS Resources

The common mock system supports realistic outputs for:

- **S3**: Buckets, versioning, encryption, public access blocks
- **DynamoDB**: Tables with attributes and billing modes
- **IAM**: Roles, policies, and policy attachments
- **Lambda**: Functions with ARNs and invoke permissions
- **API Gateway**: REST APIs, resources, methods, integrations, stages
- **Provider Calls**: CallerIdentity, regions, availability zones

#### Legacy Mock Pattern

If you need custom mocking behavior, you can still create your own:

```python
# tests/test_mymodule.py
import unittest
import pulumi
from tests.common import setup_pulumi_mocks

# Set up mocks for all tests in this module
setup_pulumi_mocks()

# Import your infrastructure modules (after mocks are set up)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'infrastructure'))
from common.mymodule import my_function

class TestMyModule(unittest.TestCase):
    @pulumi.runtime.test
    def test_something(self):
        # Your test here
        pass
```

### 2. Use Common Test Utilities

Take advantage of the centralized mocking and helper functions:

```python
from tests.common import (
    setup_pulumi_mocks, 
    get_test_mocks, 
    assert_resource_created,
    assert_resource_not_created
)

# Set up mocks
setup_pulumi_mocks()

# In your test
def test_resources_created(self):
    my_function()
    
    # Verify expected resources were created
    assert_resource_created("aws:s3/bucket:Bucket", expected_count=1)
    assert_resource_not_created("aws:s3/bucketVersioning:BucketVersioning")
```

### 3. Run Tests

```bash
poetry run pytest tests/test_mymodule.py -v
```

## Benefits of Common Mocks

1. **Consistency**: All tests use the same realistic mock responses
2. **Maintainability**: Update mock behavior in one place
3. **Reusability**: Easy to add tests for new infrastructure modules
4. **Rich Features**: Built-in resource tracking and assertion helpers
5. **Extensibility**: Easy to add support for new AWS resource types

## Resources

- [Pulumi Testing Documentation](https://www.pulumi.com/docs/iac/concepts/testing/unit/)
- [Pulumi Testing Examples](https://github.com/pulumi/examples/tree/master/testing-unit-py)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
