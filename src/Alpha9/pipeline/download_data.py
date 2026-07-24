"""
[Title] - Data Downloader

[Paragraph Description] -
Uses ccxt library to download the data for
a list of symbols of cryptocurrencies.

[Requirements] -
    None

[Usages] -
    src/Alpha9/pipeline/main_pipeline.py
"""

import logging
import time
from pathlib import Path
from typing import List, Union

import ccxt
import pandas as pd

logger = logging.getLogger(__name__)


def download(
    exchange: str,
    symbols: List[str],
    timeframe: str,
    start_date: str,
    end_date: str,
    data_dir: Union[str, Path],
) -> bool:
    """
    [Paragraph Description] -
    Downloads the historical OHLCV data for given symbols and saves them at given path.

    Args:
        exchange (str): the string identifier of the exchange.
        symbols (List[str]): the list of symbols to download against desired currency.
        timeframe (str): the timeframe to download data for.
        start_date (str): the start date to download data for (yyyy-mm-dd).
        end_date (str): the end date to download data for (yyyy-mm-dd).
        data_dir (Union[str, Path]): the directory to store the downloaded data.

    Returns:
        status (bool): whether the data downloading was successful

    Raises:
        None
    """
    try:
        exchange = getattr(ccxt, exchange)()
    except AttributeError:
        logger.error(f"Exchange '{exchange}' is not supported by ccxt!")
        return False
    except Exception as e:
        logger.exception(f"Failed to initialize exchange '{exchange}':\n{e}")
        return False

    status = True

    for symbol in symbols:
        logger.info(f"Starting download for {symbol} on {exchange}...")
        fetched_data_list = []
        try:
            start = exchange.parse8601(start_date + "T00:00:00Z")
            end = exchange.parse8601(end_date + "T23:59:59Z")

        except Exception as e:
            logger.exception(f"Failed to fetch data for {symbol}:\n{e}")
            status = False
            continue

        current_start = start
        while current_start < end:
            try:
                fetched_data_point = exchange.fetch_ohlcv(
                    symbol, timeframe=timeframe, since=current_start
                )

                if not fetched_data_point:
                    logger.info(
                        f"No more data available for {symbol} after {exchange.iso8601(current_start)}."
                    )
                    break

                fetched_data_list.extend(fetched_data_point)
                current_start = fetched_data_point[-1][0] + 1

            except ccxt.NetworkError as e:
                logger.warning(
                    f"Network error fetching {symbol}, applying backoff:\n{e}"
                )
                time.sleep(exchange.rateLimit / 1000 * 2)
                continue
            except ccxt.ExchangeError as e:
                logger.error(f"Exchange API error for {symbol}:\n{e}")
                status = False
                break
            except Exception as e:
                logger.exception(f"Unexpected error fetching {symbol}:\n{e}")
                status = False
                break

        if fetched_data_list:
            try:
                fetched_data_list = [
                    candle for candle in fetched_data_list if candle[0] <= end
                ]
                df = pd.DataFrame(
                    fetched_data_list,
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
                )
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

                file_path = data_dir / f'{symbol.split('/')[0]}.parquet'
                df.to_parquet(file_path, index=False)

                logger.info(
                    f"Successfully saved {len(df)} rows for {symbol} to {file_path}"
                )

            except Exception as e:
                logger.exception(f"Failed to process and save data for {symbol}:\n{e}")
                status = False
        else:
            logger.warning(
                f"No data was fetched for {symbol}. It may not have existed during this timeframe."
            )

    return status
