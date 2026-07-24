"""
[Title] - Launch

[Paragraph Description] -
This is the absolute cli entrypoint for the program. It handles various errors

[Requirements] -
    src/Alpha9/main.py

[Usages] -
    USER
"""

import sys

try:
    from Alpha9 import main

except ImportError as e:
    print(
        "Fatal: Failed to import 'Alpha9'. Ensure the package is installed!",
        f"Error:\n{e}",
        file=sys.stderr,
    )
    sys.exit(1)


def execute() -> None:
    """
    [Paragraph Description] -
    Invokes the applications and deals with various errors.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    try:
        main.start()

    except KeyboardInterrupt:
        print("Goodbye!", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"Critical Error:\n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    execute()
