"""
[Title] - Config Handler

[Paragraph Description] -
Handles the loading and refreshing of config files

[Requirements] -
    src/Alpha9/utility/get_path.py

[Usages] -
    notebooks/pipeline.ipynb, notebooks/backtest.ipynb
    src/Alpha9/pipeline/main_pipeline.py
    src/Alpha9/utility/read_file.py
"""

import logging
from typing import Any, Dict, Optional

import yaml

from Alpha9.utility import get_path

logger = logging.getLogger(__name__)

config_path = get_path.absolute("config.yaml")
_config: Optional[Dict[str, Any]] = None


def refresh() -> Dict[str, Any]:
    """
    [Paragraph Description] -
    Refreshes the config file, by reading from disc again

    Args:
        None

    Returns:
        config (Dict[str, Any]): the freshly loaded config file

    Raises:
        Exception: if the config file cannot be read
    """
    global _config

    try:
        with open(config_path, "r") as file:
            loaded_config = yaml.safe_load(file)

            _config = loaded_config if loaded_config is not None else {}

        logger.info(f"Successfully loaded configuration from {config_path}!")
        return _config

    except Exception as e:
        logger.critical(f"Failed to load configuration from {config_path}:\n{e}")
        raise e


def load() -> Dict[str, Any]:
    """
    [Paragraph Description] -
    loads the config file if not already loaded
    then returns the loaded config file

    Args:
        None

    Returns:
        config (Dict[str, Any]): the loaded config file

    Raises:
        None
    """
    if _config is None:
        logger.debug("Config cache is empty. Triggering initial disk read.")
        return refresh()

    return _config
