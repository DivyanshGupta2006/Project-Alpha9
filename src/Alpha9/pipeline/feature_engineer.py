"""
[Title] - Feature Engineer

[Paragraph Description] -
Uses ta-lib to calculate various technical indicators
for given list of cryptocurrency.

[Requirements] -
    None

[Usages] -
    src/Alpha9/pipeline/main_pipeline.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Union

import numpy as np
import pandas as pd
import talib as ta

logger = logging.getLogger(__name__)


def ICHIMOKU(
    high_px: pd.Series,
    low_px: pd.Series,
    close_px: pd.Series,
    fastperiod: int,
    medperiod: int,
    slowperiod: int,
) -> tuple:
    """
    [Paragraph Description] -
    Calculates the Ichimoku-Cloud technical indicators

    Args:
        high_px (pd.Series): the high price series.
        low_px (pd.Series): the low price series.
        close_px (pd.Series): the close price series.
        fastperiod (int): the fast timeperiod value.
        medperiod (int): the medium timeperiod value.
        slowperiod (int): the slow timeperiod value.

    Returns:
        (cloud_trend, tk_cross) (tuple): the Ichimoku-Cloud technical indicators

    Raises:
        None
    """
    tenkan = (
        ta.MAX(high_px, timeperiod=fastperiod) + ta.MIN(low_px, timeperiod=fastperiod)
    ) / 2
    kijun = (
        ta.MAX(high_px, timeperiod=medperiod) + ta.MIN(low_px, timeperiod=medperiod)
    ) / 2
    span_b = (
        ta.MAX(high_px, timeperiod=slowperiod) + ta.MIN(low_px, timeperiod=slowperiod)
    ) / 2

    cloud_trend = np.where(close_px != 0, (close_px - span_b) / close_px, 0)
    tk_cross = np.where(close_px != 0, (tenkan - kijun) / close_px, 0)

    return cloud_trend, tk_cross


def VWAP(
    high_px: pd.Series,
    low_px: pd.Series,
    close_px: pd.Series,
    vol: pd.Series,
    period: int,
) -> pd.Series:
    """
    [Paragraph Description] -
    Calculates the VWAP technical indicator

    Args:
        high_px (pd.Series): the high price series.
        low_px (pd.Series): the low price series.
        close_px (pd.Series): the close price series.
        vol (pd.Series): the volume series.
        period (int): the period value.

    Returns:
        vwap (pd.Series): the VWAP technical indicator

    Raises:
        None
    """
    typical_price = (high_px + low_px + close_px) / 3
    pv = typical_price * vol

    pv_sum = pv.rolling(window=period, min_periods=period).sum()
    vol_sum = vol.rolling(window=period, min_periods=period).sum()
    vwap = pv_sum / vol_sum.replace(0, np.nan)
    return vwap


def engineer(
    data: Dict[str, pd.DataFrame],
    symbols: List[str],
    timeperiod_cat: int,
    timeperiod_cat0: int,
    timeperiod_cat1: int,
    timeperiod_cat2: int,
    timeperiod_cat3: int,
    timeperiod_cat4: int,
    selected_features: List[str],
    data_dir: Union[str, Path],
) -> bool:
    """
    [Paragraph Description] -
    Computes features (technical indicators) for each given symbol and saves at given path.

    Args:
        data (Dict[str, pd.DataFrame]): the data for each symbol, arranged in dict.
        symbols (List[str]): the list of symbols.
        timeperiod_cat (int): the time period of the technical indicators of category.
        timeperiod_cat0 (int): the time period of the technical indicators of category 0.
        timeperiod_cat1 (int): the time period of the technical indicators of category 1.
        timeperiod_cat2 (int): the time period of the technical indicators of category 2.
        timeperiod_cat3 (int): the time period of the technical indicators of category 3.
        timeperiod_cat4 (int): the time period of the technical indicators of category 4.
        selected_features (List[str]): the list of selected features that need to be included.
        data_dir (Union[str, Path]): the directory to store the featured data.

    Returns:
        status (bool): whether the feature engineering for each symbol was successful

    Raises:
        [error_name: description]
    """
    status = True
    for symbol in symbols:
        if symbol not in data:
            logger.error(f"Symbol {symbol} not found in data")
            status = False
            continue

        logger.info(f"Computing features for {symbol}")

        try:
            featured_data = data[symbol].copy()

            open_px = featured_data["open"].astype(float)
            high_px = featured_data["high"].astype(float)
            low_px = featured_data["low"].astype(float)
            close_px = featured_data["close"].astype(float)
            vol = featured_data["volume"].astype(float)

            # trend indicators
            featured_data["sma-dist"] = (
                close_px - ta.SMA(close_px, timeperiod=timeperiod_cat4)
            ) / ta.SMA(close_px, timeperiod=timeperiod_cat4)
            featured_data["ema-dist"] = (
                close_px - ta.EMA(close_px, timeperiod=timeperiod_cat3)
            ) / ta.EMA(close_px, timeperiod=timeperiod_cat3)

            macd, macdsignal, macdhist = ta.MACD(
                close_px,
                fastperiod=timeperiod_cat1,
                slowperiod=timeperiod_cat3,
                signalperiod=timeperiod_cat0,
            )
            featured_data["macd-signal-pct"] = np.where(
                close_px != 0, (macd - macdsignal) / close_px, 0
            )
            featured_data["macd-slope"] = macd.diff()

            featured_data["trix"] = ta.TRIX(close_px, timeperiod=timeperiod_cat2)
            featured_data["sar"] = (close_px - ta.SAR(high_px, low_px)) / close_px
            featured_data["tema"] = (
                close_px - ta.TEMA(close_px, timeperiod=timeperiod_cat2)
            ) / ta.TEMA(close_px, timeperiod=timeperiod_cat2)
            featured_data["trima"] = ta.TRIMA(close_px, timeperiod=timeperiod_cat4)
            featured_data["wma"] = ta.WMA(close_px, timeperiod=timeperiod_cat3)
            featured_data["dema"] = (
                close_px - ta.DEMA(close_px, timeperiod=timeperiod_cat4)
            ) / ta.DEMA(close_px, timeperiod=timeperiod_cat4)

            featured_data["ppo"] = ta.PPO(
                close_px, fastperiod=timeperiod_cat1, slowperiod=timeperiod_cat3
            )
            featured_data["plus-di"] = ta.PLUS_DI(
                high_px, low_px, close_px, timeperiod=timeperiod_cat0
            )
            featured_data["minus-di"] = ta.MINUS_DI(
                high_px, low_px, close_px, timeperiod=timeperiod_cat0
            )
            featured_data["lin-reg-slope"] = ta.LINEARREG_SLOPE(
                close_px, timeperiod=timeperiod_cat2
            )
            featured_data["ichi-cloud-trend"], featured_data["ichi-tk-cross"] = (
                ICHIMOKU(
                    high_px,
                    low_px,
                    close_px,
                    timeperiod_cat0,
                    timeperiod_cat3,
                    timeperiod_cat4,
                )
            )

            # momentum indicators
            featured_data["rsi"] = ta.RSI(close_px, timeperiod=timeperiod_cat2)
            featured_data["stoch-osc-slowk"], featured_data["stoch-osc-slowd"] = (
                ta.STOCH(
                    high_px,
                    low_px,
                    close_px,
                    fastk_period=timeperiod_cat2,
                    slowk_period=timeperiod_cat,
                    slowd_period=timeperiod_cat,
                )
            )
            featured_data["adx"] = ta.ADX(
                high_px, low_px, close_px, timeperiod=timeperiod_cat2
            )
            featured_data["momentum"] = ta.MOM(close_px, timeperiod=timeperiod_cat2)
            featured_data["cci"] = ta.CCI(
                high_px, low_px, close_px, timeperiod=timeperiod_cat2
            )
            featured_data["cmo"] = ta.CMO(close_px, timeperiod=timeperiod_cat2)
            fastk, fastd = ta.STOCHRSI(
                close_px,
                timeperiod=timeperiod_cat2,
                fastk_period=timeperiod_cat2,
                fastd_period=timeperiod_cat,
            )
            featured_data["stoch-rsi"] = fastk - fastd
            featured_data["williams-%r"] = ta.WILLR(
                high_px, low_px, close_px, timeperiod=timeperiod_cat2
            )
            featured_data["bop"] = ta.BOP(open_px, high_px, low_px, close_px)

            # volatility indicators
            featured_data["natr"] = ta.NATR(
                high_px, low_px, close_px, timeperiod=timeperiod_cat2
            )
            upper, middle, lower = ta.BBANDS(close_px, timeperiod=timeperiod_cat3)
            featured_data["bbands_pct"] = (close_px - lower) / (upper - lower)
            featured_data["bbands_width"] = (upper - lower) / middle
            featured_data["std-dev"] = ta.STDDEV(
                np.log(close_px), timeperiod=timeperiod_cat3
            )

            # volume indicators
            featured_data["obv"] = ta.OBV(close_px, vol)
            featured_data["vwap"] = VWAP(
                high_px, low_px, close_px, vol, timeperiod_cat3
            )
            featured_data["mfi"] = ta.MFI(
                high_px, low_px, close_px, vol, timeperiod=timeperiod_cat2
            )
            featured_data["ad-line"] = ta.AD(high_px, low_px, close_px, vol)

            # basic indicators
            featured_data["log-return"] = np.log(close_px / close_px.shift(1))
            featured_data["vol-spike"] = (
                vol - vol.rolling(timeperiod_cat2).mean()
            ) / vol.rolling(timeperiod_cat2).mean()
            featured_data["norm-volatility"] = (high_px - low_px) / close_px

            # drop column(s)
            cols = [
                col
                for col in list(featured_data.columns)
                if col not in selected_features
            ]
            featured_data = featured_data[cols]
            featured_data = featured_data.dropna()
            featured_data.to_parquet(data_dir / f"{symbol}.parquet", index=True)
            logger.info(
                f"Successfully saved {len(featured_data)} feature rows for {symbol}."
            )

        except Exception as e:
            logger.exception(
                f"Unexpected error while computing features for {symbol}:\n{e}"
            )
            status = False

    return status
