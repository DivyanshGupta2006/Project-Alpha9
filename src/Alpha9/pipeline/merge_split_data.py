"""
[Title] - Split and Merge

[Paragraph Description] -
Uses internal functions of pandas to merge the data of all cryptocurrencies
and split the resultant into train, validation and test sets.

[Requirements] -
    None

[Usages] -
    src/Alpha9/pipeline/main_pipeline.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

logger = logging.getLogger(__name__)


def merge_split(
    data: Dict[str, pd.DataFrame],
    symbols: List[str],
    train_start_date: str,
    val_start_date: str,
    test_start_date: str,
    train_dir: Union[str, Path],
    val_dir: Union[str, Path],
    test_dir: Union[str, Path],
) -> bool:
    """
    [Paragraph Description] -
    Performs merge on data of all cryptocurrencies and
    splits the resultant into train, validation and test sets.

    Args:
        data (Dict[str, pd.DataFrame]): featured data for each symbol, arranged in dict.
        symbols (List[str]): list of all symbols.
        train_start_date (str): start date of training data (yyyy-mm-dd).
        val_start_date (str): start date of validation data (yyyy-mm-dd).
        test_start_date (str): start date of test data (yyyy-mm-dd).
        train_dir (Union[str, Path]): the directory to store the training data.
        val_dir (Union[str, Path]): the directory to store the validation data.
        test_dir (Union[str, Path]): the directory to store the test data.

    Returns:
        status (bool): whether the merge and split was successful

    Raises:
        None
    """

    logger.info("Starting merge and split process...")
    dfs = []
    merged_data = pd.DataFrame()
    status = True

    # merge
    for symbol in symbols:
        if symbol not in data:
            logger.warning(f"Symbol '{symbol}' not found in data")
            status = False
            continue

        try:
            df = data[symbol].copy()
            df.columns = pd.MultiIndex.from_product([df.columns, [symbol]])
            dfs.append(df)

        except Exception as e:
            logger.exception(f"Error while merging {symbol}: {e}")
            status = False
            continue

    if not dfs:
        logger.error("No valid DataFrames were found to merge!")
        return False

    try:
        logger.info("Concatenating...")
        merged_data = pd.concat(dfs, axis=1, join="inner")

        initial_len = len(merged_data)
        logger.info(f"Initial length: {initial_len}")

        merged_data = merged_data.dropna()
        final_len = len(merged_data)
        logger.info(f"Final length: {final_len}")
        logger.info(f"Dropped {final_len - initial_len} rows")

        if merged_data.empty:
            logger.error("Merged DataFrame is empty!")
            return False

    except Exception as e:
        logger.exception(f"Error while merging: {e}")
        return False

        # split
    try:
        data_train = merged_data[
            (train_start_date <= merged_data.index)
            & (merged_data.index < val_start_date)
        ]
        data_val = merged_data[
            (val_start_date <= merged_data.index)
            & (merged_data.index < test_start_date)
        ]
        data_test = merged_data[(test_start_date <= merged_data.index)]

        data_train.to_parquet(train_dir / "data.parquet", index=True)
        logger.info(f"Train data: {len(data_train)} rows saved to {train_dir}")
        data_val.to_parquet(val_dir / "data.parquet", index=True)
        logger.info(f"Validation data: {len(data_val)} rows saved to {val_dir}")
        data_test.to_parquet(test_dir / "data.parquet", index=True)
        logger.info(f"Test data: {len(data_test)} rows saved to {test_dir}")

    except Exception as e:
        logger.exception(f"Error while splitting and/or saving: {e}")
        return False

    return status
