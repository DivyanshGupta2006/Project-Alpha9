"""
[Title] - Path Handler

[Paragraph Description] -
Handles all the path related operations

[Requirements] -
    None

[Usages] -
    notebooks/pipeline.ipynb, notebooks/backtest.ipynb
    src/Alpha9/pipeline/main_pipeline.py
    src/Alpha9/utility/get_config.py
    src/Alpha9/utility/read_file.py
"""

import logging
import os
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def check(directory: Union[str, Path]) -> None:
    """
    [Paragraph Description] -
    Checks whether the passed directory exists or not
    If it doesn't, it creates that directory

    Args:
        directory (Union[str, Path]): the directory to check

    Returns:
        None

    Raises:
        None
    """
    logger.debug(f"Checking directory {directory}")
    os.makedirs(directory, exist_ok=True)


def absolute(path: Union[str, Path]) -> Path:
    """
    [Paragraph Description] -
    Returns the absolute path of the given path

    Args:
        path (Union[str, Path]): the path, of which the absolute path is required

    Returns:
        target (Path): the absolute path of the passed path

    Raises:
        None
    """
    target = PROJECT_ROOT.joinpath(path)
    logger.debug(f"Absolute path for {path} -> {target}")
    return target
