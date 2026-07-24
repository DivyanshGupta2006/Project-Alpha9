"""
[Title] - Pipeline Orchestrator

[Paragraph Description] -
Handles the calls to all the individual pipeline components.

[Requirements] -
    src/Alpha9/pipeline/download_data.py, src/Alpha9/pipeline/feature_engineer.py,
    src/Alpha9/pipeline/merge_split_data.py
    src/Alpha9/utility/get_path.py, src/Alpha9/utility/get_config.py, src/Alpha9/utility/read_file.py

[Usages] -
    src/Alpha9/main.py
"""

import logging
from typing import Dict

import pandas as pd

from Alpha9.pipeline import download_data, feature_engineer, merge_split_data
from Alpha9.utility import get_config, get_path, read_file

logger = logging.getLogger(__name__)


def run(force_download: bool = False) -> bool:
    """
    [Paragraph Description] -
    Calls all the individual pipeline components.

    Args:
        force_download (bool, optional): Whether to force download of data. Defaults to False.

    Returns:
        status (bool): Whether the pipeline run was successful or not.

    Raises:
        None
    """
    logger.info("Initializing pipeline...")

    try:
        config = get_config.load()

        # load and handle paths
        paths = config["path"]["data"]
        raw_data_dir = get_path.absolute(paths["raw"])
        featured_data_dir = get_path.absolute(paths["featured"])
        train_data_dir = get_path.absolute(paths["train"])
        val_data_dir = get_path.absolute(paths["val"])
        test_data_dir = get_path.absolute(paths["test"])

        for directory in [
            raw_data_dir,
            featured_data_dir,
            train_data_dir,
            val_data_dir,
            test_data_dir,
        ]:
            get_path.check(directory)

        logger.info("Loaded all the paths!")

        # load and handle data downloading constants
        exchange = config["pipeline"]["exchange"]
        symbols = config["pipeline"]["symbols"]
        timeframe = config["pipeline"]["timeframe"]
        start_date = config["pipeline"]["start_date"]
        end_date = config["pipeline"]["end_date"]

        # load and handle feature engineering constants
        timeperiod_cat = config["pipeline"]["timeperiod_cat"]
        timeperiod_cat0 = config["pipeline"]["timeperiod_cat0"]
        timeperiod_cat1 = config["pipeline"]["timeperiod_cat1"]
        timeperiod_cat2 = config["pipeline"]["timeperiod_cat2"]
        timeperiod_cat3 = config["pipeline"]["timeperiod_cat3"]
        timeperiod_cat4 = config["pipeline"]["timeperiod_cat4"]
        selected_features = config["pipeline"]["selected_features"]

        # load and handle merge and split constants
        train_start_date = config["pipeline"]["train_start_date"]
        val_start_date = config["pipeline"]["val_start_date"]
        test_start_date = config["pipeline"]["test_start_date"]

        logger.info("Loaded other piepline config constants!")

    except KeyError as e:
        logger.error(f"Configuration is missing a required key: \n{e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during pipeline initialization: \n{e}")
        return False

    if force_download:
        logger.info(
            f"Starting data download from {exchange.upper()} for {len(symbols)} symbols..."
        )

        status = download_data.download(
            exchange, symbols, timeframe, start_date, end_date, raw_data_dir
        )
        if status:
            logger.info("Successfully downloaded all historical data!")
        else:
            logger.error("Failed to download data. Aborting pipeline.")
            return False
    else:
        logger.info("Using pre-downloaded raw data...")

    # handle feature engineering
    logger.info("Creating features...")
    data: Dict[str, pd.DataFrame] = {}

    # remove '/USDT' from the symbols (redundant)
    symbols = [symbol.split("/")[0] for symbol in symbols]

    for symbol in symbols:
        df = read_file.read_data("raw", symbol)
        if df is None or df.empty:
            logger.error(f"Raw data for {symbol} could not be loaded. Aborting!")
            return False
        data[symbol] = df

    status = feature_engineer.engineer(
        data,
        symbols,
        timeperiod_cat,
        timeperiod_cat0,
        timeperiod_cat1,
        timeperiod_cat2,
        timeperiod_cat3,
        timeperiod_cat4,
        selected_features,
        featured_data_dir,
    )

    if status:
        logger.info("Successfully engineered all features!")
    else:
        logger.error("Failed to engineer features. Aborting pipeline.")
        return False

    # handle merge & split
    logger.info("Performing Merge & Split")
    data: Dict[str, pd.DataFrame] = {}

    for symbol in symbols:
        df = read_file.read_data("featured", symbol)
        if df is None or df.empty:
            logger.error(f"Featured data for {symbol} could not be loaded. Aborting!")
            return False
        data[symbol] = df

    status = merge_split_data.merge_split(
        data,
        symbols,
        train_start_date,
        val_start_date,
        test_start_date,
        train_data_dir,
        val_data_dir,
        test_data_dir,
    )

    if status:
        logger.info("Successfully performed Merge & Split!")
    else:
        logger.error("Failed to perform Merge & Split. Aborting pipeline.")
        return False

    logger.info("Pipeline run successful!")

    return True
