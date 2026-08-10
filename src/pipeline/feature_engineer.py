import talib as ta
import numpy as np

def ICHIMOKU(high_px, low_px, close_px, fastperiod, medperiod, slowperiod):
    tenkan = (ta.MAX(high_px, timeperiod=fastperiod) + ta.MIN(low_px, timeperiod=fastperiod)) / 2
    kijun = (ta.MAX(high_px, timeperiod=medperiod) + ta.MIN(low_px, timeperiod=medperiod)) / 2
    span_b = (ta.MAX(high_px, timeperiod=slowperiod) + ta.MIN(low_px, timeperiod=slowperiod)) / 2
    cloud_trend = (close_px - span_b) / close_px
    tk_cross = (tenkan - kijun) / close_px
    return cloud_trend, tk_cross

def VWAP(high_px, low_px, close_px, vol, period):
    typical_price = (high_px + low_px + close_px) / 3
    pv = typical_price * vol
    pv_sum = pv.rolling(window=period, min_periods=period).sum()
    vol_sum = vol.rolling(window=period, min_periods=period).sum()

    return pv_sum / vol_sum

def engineer(data,
             symbols,
             timeperiod_cat,
             timeperiod_cat0,
             timeperiod_cat1,
             timeperiod_cat2,
             timeperiod_cat3,
             timeperiod_cat4,
             selected_features,
             data_dir):
    for symbol in symbols:
        featured_data = data[symbol]

        open_px = featured_data['open']
        high_px = featured_data['high']
        low_px = featured_data['low']
        close_px = featured_data['close']
        vol = featured_data['volume']

        # trend indicators
        featured_data['sma-dist'] = (close_px - ta.SMA(close_px, timeperiod=timeperiod_cat4)) / ta.SMA(close_px,
                                                                                              timeperiod=timeperiod_cat4)
        featured_data['ema-dist'] = (close_px - ta.EMA(close_px, timeperiod=timeperiod_cat3)) / ta.EMA(close_px,
                                                                                              timeperiod=timeperiod_cat3)
        macd, macdsignal, macdhist = ta.MACD(close_px, fastperiod=timeperiod_cat1, slowperiod=timeperiod_cat3,
                                             signalperiod=timeperiod_cat0)
        featured_data['macd-signal-pct'] = (macd - macdsignal) / close_px
        featured_data['macd-slope'] = macd.diff()
        featured_data['trix'] = ta.TRIX(close_px, timeperiod=timeperiod_cat2)
        featured_data['sar'] = (close_px - ta.SAR(high_px, low_px)) / close_px
        featured_data['tema'] = (close_px - ta.TEMA(close_px, timeperiod=timeperiod_cat2)) / ta.TEMA(close_px,
                                                                                            timeperiod=timeperiod_cat2)
        featured_data['trima'] = ta.TRIMA(close_px, timeperiod=timeperiod_cat4)
        featured_data['wma'] = ta.WMA(close_px, timeperiod=timeperiod_cat3)
        featured_data['dema'] = (close_px - ta.DEMA(close_px, timeperiod=timeperiod_cat4)) / ta.DEMA(close_px,
                                                                                            timeperiod=timeperiod_cat4)
        featured_data['ppo'] = ta.PPO(close_px, fastperiod=timeperiod_cat1, slowperiod=timeperiod_cat3)
        featured_data['plus-di'] = ta.PLUS_DI(high_px, low_px, close_px, timeperiod=timeperiod_cat0)
        featured_data['minus-di'] = ta.MINUS_DI(high_px, low_px, close_px, timeperiod=timeperiod_cat0)
        featured_data['lin-reg-slope'] = ta.LINEARREG_SLOPE(close_px, timeperiod=timeperiod_cat2)
        featured_data['ichi-cloud-trend'], featured_data['ichi-tk-cross'] = ICHIMOKU(high_px, low_px, close_px, timeperiod_cat0,
                                                                   timeperiod_cat3, timeperiod_cat4)

        # momentum indicators
        featured_data['rsi'] = ta.RSI(close_px, timeperiod=timeperiod_cat2)
        featured_data['stoch-osc-slowk'], featured_data['stoch-osc-slowd'] = ta.STOCH(high_px, low_px, close_px,
                                                                    fastk_period=timeperiod_cat2,
                                                                    slowk_period=timeperiod_cat,
                                                                    slowd_period=timeperiod_cat)
        featured_data['adx'] = ta.ADX(high_px, low_px, close_px, timeperiod=timeperiod_cat2)
        featured_data['momentum'] = ta.MOM(close_px, timeperiod=timeperiod_cat2)
        featured_data['cci'] = ta.CCI(high_px, low_px, close_px, timeperiod=timeperiod_cat2)
        featured_data['cmo'] = ta.CMO(close_px, timeperiod=timeperiod_cat2)
        fastk, fastd = ta.STOCHRSI(close_px, timeperiod=timeperiod_cat2, fastk_period=timeperiod_cat2,
                                   fastd_period=timeperiod_cat)
        featured_data['stoch-rsi'] = fastk - fastd
        featured_data['williams-%r'] = ta.WILLR(high_px, low_px, close_px, timeperiod=timeperiod_cat2)
        featured_data['bop'] = ta.BOP(open_px, high_px, low_px, close_px)

        # volatility indicators
        featured_data['natr'] = ta.NATR(high_px, low_px, close_px, timeperiod=timeperiod_cat2)
        upper, middle, lower = ta.BBANDS(close_px, timeperiod=timeperiod_cat3)
        featured_data['bbands_pct'] = (close_px - lower) / (upper - lower)
        featured_data['bbands_width'] = (upper - lower) / middle
        featured_data['std-dev'] = ta.STDDEV(np.log(close_px), timeperiod=timeperiod_cat3)

        # volume indicators
        featured_data['obv'] = ta.OBV(close_px, vol)
        featured_data['vwap'] = VWAP(high_px, low_px, close_px, vol, timeperiod_cat3)
        featured_data['mfi'] = ta.MFI(high_px, low_px, close_px, vol, timeperiod=timeperiod_cat2)
        featured_data['ad-line'] = ta.AD(high_px, low_px, close_px, vol)

        # basic indicators
        featured_data['log-return'] = (np.log(close_px / close_px.shift(1)))
        featured_data['vol-spike'] = (vol - vol.rolling(timeperiod_cat2).mean()) / vol.rolling(timeperiod_cat2).mean()
        featured_data['norm-volatility'] = ((high_px - low_px) / close_px)

        # drop column(s) if required
        featured_data.drop(columns=[col for col in list(featured_data.columns) if col not in selected_features], inplace=True)

        featured_data.dropna(inplace=True)
        featured_data.to_csv(data_dir / f'{symbol}.csv', index=True)
    return "Success"