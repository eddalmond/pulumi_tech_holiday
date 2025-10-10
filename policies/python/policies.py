from collections.abc import Mapping

from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)


def ensure_managed_by_tag(props: Mapping[str, object]) -> str | None:
    """Check that resources include a ManagedBy tag."""
    tags = props.get("tags") or {}
    if not isinstance(tags, Mapping):
        return "Expected tags to be a mapping"

    if "ManagedBy" not in tags:
        return "Resource should include a 'ManagedBy' tag to denote ownership."

    return None


def _s3_managed_by_tag_validator(
    args: ResourceValidationArgs, report: ReportViolation
) -> None:
    if args.resource_type != "aws:s3/bucket:Bucket":
        return

    message = ensure_managed_by_tag(args.props)
    if message:
        report(message)


def register_policy_pack() -> None:
    """Register the Python policy pack used in CI and local previews."""
    PolicyPack(
        name="python-guardrails",
        policies=[
            ResourceValidationPolicy(
                name="s3-managed-by-tag",
                description="Ensure S3 buckets include the ManagedBy tag for ownership tracking.",
                validate=_s3_managed_by_tag_validator,
                enforcement_level=EnforcementLevel.ADVISORY,
            ),
        ],
    )
