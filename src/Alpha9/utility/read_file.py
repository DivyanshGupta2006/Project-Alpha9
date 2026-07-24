"""
[Title] - File Parser

[Paragraph Description] -
Returns the file after reading it from requested directory

[Requirements] -
    src/Alpha9/utility/get_path.py, src/Alpha9/utility/get_config.py

[Usages] -
    notebooks/pipeline.ipynb, notebooks/backtest.ipynb
    src/Alpha9/pipeline/main_pipeline.py
"""

import logging
from typing import Optional

import pandas as pd

from Alpha9.utility import get_config, get_path

logger = logging.getLogger(__name__)


def read_data(data_type: str, file: str) -> Optional[pd.DataFrame]:
    """
    [Paragraph Description] -
    Returns the file after reading it from requested directory

    Args:
        data_type (str): the broader directory for data
        file (str): the file name from data_type directory

    Returns:
        data (Optional[pd.DataFrame]): the file after reading it from requested directory, if no exceptions raised

    Raises:
        Exception: if the file cannot be read
    """
    try:
        config = get_config.load()
        data_dir = get_path.absolute(config["path"]["data"][data_type])
        file = f'{file.split('/')[0]}.parquet'
        path = data_dir / file

        if not path.exists():
            logger.error(f"File not found: {path}")
            return None

        data = pd.read_parquet(path)

        # index management
        if "timestamp" in data.columns and data.index.name != "timestamp":
            data.set_index("timestamp", inplace=True)

        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)

        logger.debug(f"Successfully loaded {len(data)} rows for {file} ({data_type})")
        return data

    except Exception as e:
        logger.exception(f"Exception while reading {file} ({data_type}):\n{e}")
        raise e
