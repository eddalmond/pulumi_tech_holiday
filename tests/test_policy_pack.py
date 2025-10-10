import pytest

from policies.python.policies import ensure_managed_by_tag


@pytest.mark.unit
@pytest.mark.parametrize(
    ["tags", "expected"],
    [
        ({"ManagedBy": "Pulumi"}, None),
        (
            {"Owner": "Team"},
            "Resource should include a 'ManagedBy' tag to denote ownership.",
        ),
        ({}, "Resource should include a 'ManagedBy' tag to denote ownership."),
    ],
)
def test_ensure_managed_by_tag(tags, expected):
    assert ensure_managed_by_tag({"tags": tags or {}}) == expected
