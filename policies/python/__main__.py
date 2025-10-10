import sys
from pathlib import Path


def _register() -> None:
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    from policies import register_policy_pack  # type: ignore import

    register_policy_pack()


if __name__ == "__main__":
    _register()
