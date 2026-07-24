"""
[Title] - Package installer

[Paragraph Description] -
Installs the package and all related dependencies.
Resolves the errors that occur during the installation.

[Requirements] -
    None

[Usages] -
    USER
"""

import subprocess
import sys


def run():
    """
    [Paragraph Description] -
    Installs the package and all related dependencies.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("Installing Alpha9 (and dependencies)...")

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-e",
        ".",
        "--extra-index-url",
        "https://download.pytorch.org/whl/cu126",
    ]

    try:
        subprocess.check_call(command)
        print("\nInstallation complete!")
        sys.exit(0)

    except subprocess.CalledProcessError as e:
        print(f"Unexpected error during installation : \n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
