# Initial setup / background

## Environment

I’m using a WSL2 Ubuntu 24.4 image from the Microsoft Store / WSL command line

## AWS account

Signed up for a new AWS account using a new email address, completed a ‘challenge’ (EC2) to get $20 credit to play with. Realised I also have $100 for setting up a new account. Should be enough!

## Repository Setup

https://github.com/eddalmond/pulumi_tech_holiday

I asked Claude for advice on Repository setup. I will be using my personal GitHub account.

[Repository Setup for Pulumi](https://www.notion.so/Repository-Setup-for-Pulumi-2868952e8eb8804e9132c8799e62b3c8?pvs=21)

I gave the same prompt to Github Copilot, asking it to help with repository set up. It has started working on an MR which I’ll review versus best practice documentation.

I then set up Poetry as python package manager, as I’m used to working with it. Github CoPilot review had no issues.

# Initialising pulumi

## Create a project

https://www.pulumi.com/docs/iac/concepts/projects/

Created a Pulumi.yaml file with basic config:

```yaml
name: pulumi_tech_holiday
description: Simple API with AWS API Gateway, Lambda, S3, and DynamoDB
runtime: python
toolchain: poetry
main: .

```

[`README.md`](http://readme.md/) has details of how to install pre-requisites

## Create a stack (or stacks!)

From [`readme.md`](http://readme.md) :

`poetry run pulumi stack init dev` - where `dev` is stack name. Creating a stack needs an associated passphrase, which can be referenced via environment variables e.g. `PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE`

We can reference the active stack with:

`stack_name = pulumi.get_stack()`

So can write simple switching logic to deploy specific stacks.

> [!TIP]
> 💡 Need to investigate how we can switch stacks in both local and GitHub Actions / other CI/CD

## Bootstrap stack

I chose to have a couple of stacks:

1. A stack to set up state tracking in s3 plus DynamoDB.
2. A second stack which contains the main application infrastructure

```python
# Deploy bootstrap (uses local state)
pulumi login --local
pulumi stack select bootstrap
pulumi up

# Deploy application stacks (uses S3 state)
pulumi login s3://pulumi-state-007027391700-eu-west-2  
pulumi stack select dev  # or staging, prod, etc.
pulumi up
```

> [!TIP]
> 💡 I should work out how to not hardcode the state bucket name for other commands - does it need outputting from bootstrap and then make available else
>
> A: Presumably I can use the `pulumi.export` stuff below

Created a `deploy_bootstrap_stack` function to deal with creating the s3 bucket and associated lock record in dynamoDB in `src/**main**.py`

This is created with a local state file. In order to transfer to s3:

1. Log into local state: `poetry run pulumi login --local`
2. Select bootstrap stack: `poetry run pulumi stack select bootstrap`
3. Export the local state to a file: `poetry run pulumi stack export --file bootstrap-state.json`
4. Log into remote state: `poetry run pulumi login s3://pulumi-state-007027391700-eu-west-2`
5. Initialise bootstrap state remotely: `poetry run pulumi stack init bootstrap`
6. Import the local state file: `poetry run pulumi stack import --file bootstrap-state.json`
7. Deploy the bootstrap layer: `poetry run pulumi up`

Cleanup:

1. Log into local state - `poetry run pulumi login --local`
2. Delete state - `poetry run pulumi stack rm bootstrap --force`
3. Remove the exported state file - `rm bootstrap-state.json`

Check remote states:

1. Login: `poetry run pulumi login s3://pulumi-state-007027391700-eu-west-2`
2. List stacks to confirm: `poetry run pulumi stack ls`

> [!TIP]
> 💡 Look into S3 lock file rather than DynamoDB

## Application stack

Application contains:

- API Gateway + routing
- Lambda
- DynamoDB
- s3

## Destroying stacks

At the end of the day, to avoid using all my credits:

`poetry run pulumi destroy`

## Refactoring

Working on refactoring a long list of sequential actions into common function/classes (to allow creation of s3 etc. without replicating code, where there’s mostly common use cases.

Aim is to then see if we can do unit testing on these functions and classes.

> [!TIP]
> 💡 Do Pulumi resource calls actually return anything? For example: `public_access_block = aws.s3.BucketPublicAccessBlock(...)`
>
> **Answer**
>
> All [input](https://www.pulumi.com/registry/packages/aws/api-docs/s3/bucketpublicaccessblock/#inputs) properties are implicitly available as output properties. Additionally, the `BucketPublicAccessBlock` resource produces the following output properties:
>
> - [`id`](https://www.pulumi.com/registry/packages/aws/api-docs/s3/bucketpublicaccessblock/#id_python) (`str`): The provider-assigned unique ID for this managed resource.
>
> Also, there’s a `.get` method:
>
> ```python
> @staticmethod
> def get(
>     resource_name: str,
>     id: str,
>     opts: Optional[ResourceOptions] = None,
>     block_public_acls: Optional[bool] = None,
>     block_public_policy: Optional[bool] = None,
>     bucket: Optional[str] = None,
>     ignore_public_acls: Optional[bool] = None,
>     region: Optional[str] = None,
>     restrict_public_buckets: Optional[bool] = None,
>     skip_destroy: Optional[bool] = None,
> ) -> BucketPublicAccessBlock
> ```

> [!TIP]
> 💡 What does `pulumi.export` do?
>
> **Answer**
>
> `pulumi.export` creates **stack outputs**—named values that are stored with the stack's state and can be accessed later.
>
> **How exports work:**
>
> 1. **Stored in stack state**: Exports are saved in the stack's state file (local or S3).
> 2. **Accessible via CLI**: You can view them with `pulumi stack output`.
> 3. **Cross-stack references**: Other stacks can read these values.
> 4. **Persistent**: They remain available until the stack is destroyed.

## Unit Testing

There’s some value to pulumi in terms of unit testing. Amenable to patching/mocks via `pulumi.runtime.Mocks` ,so can test *implementation* logic separately to actual infrastructure deployment.

I’ve implemented a basic test mock class for some of the services I use, so I can explore this a bit further.

## CI/CD and tooling

Adding in some standard security + linting + test running via Github Actions

👎 Checkov, TFSec etc.  - standard tooling is not integrated with pulumi, so looking into alternatives

> [!TIP]
> 💡 Looking into AWS Guard and Pulumi Policy
>
> Implemented both, as they cover slightly different contexts:
>
> - AWS Guard has prebuilt sets of policies you can configure (for example mandatory vs. warning).
> - Pulumi Policy lets you set up custom policies.
>
> Both together might be overkill, but building up the latter is likely easier than the former, so I’d view AWS Guard as guard rails based on AWS best practice, then use Pulumi Policy for organisation-specific security.

## To do

1. Add in type checking etc. - done by mypy, but could I use Pydantic?
2. Integration testing
3. Stretch goal is in .md - adding VPC + SSM + other bits
