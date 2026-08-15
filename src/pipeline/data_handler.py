import ast

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from market.events import MarketEvent
from market.schemas import AbstractDataHandler

sns.set_theme(style="darkgrid")


class DataHandler(AbstractDataHandler):
    def __init__(self, data, symbols, event_queue, start_date, end_date):
        self.data = data.truncate(before=start_date, after=end_date)
        cols = []
        for col in self.data.columns:
            if isinstance(col, str):
                col = ast.literal_eval(col)
            cols.append(col)
        self.data.columns = cols
        self.symbols = symbols
        self.event_queue = event_queue
        self.start_date = start_date
        self.end_date = end_date
        self.continue_backtest = True
        self.latest_data = {}
        self._data_index = None
        self._iter_timesteps = None

        self._prepare_data_iterator()

    # private methods for creating the required methods
    def _prepare_data_iterator(self):
        all_timesteps = sorted(list(set(self.data.index)))
        self._iter_timesteps = iter(all_timesteps)

    def _get_candle(self, timestamp):
        try:
            candle = self.data.loc[timestamp]
            if not candle.isnull().all():
                return candle
        except KeyError:
            pass
        return None

    def update_candles(self):
        if self._iter_timesteps is None:
            self.continue_backtest = False
            return

        try:
            current_date = next(self._iter_timesteps)
        except StopIteration:
            self.continue_backtest = False
            return

        candle = self._get_candle(current_date)
        if candle is not None:
            self.latest_data = candle
            market_event = MarketEvent(timestamp=current_date)
            self.event_queue.put_event(market_event)

    def get_latest_candle(self):
        return self.latest_data

    def get_latest_candles(self, N=1):
        latest_date = self.get_latest_candle_datetime()
        if latest_date:
            try:
                loc = self.data.index.get_loc(latest_date)
                start_loc = max(0, loc - N + 1)
                return self.data.iloc[start_loc : loc + 1]
            except KeyError:
                print(f"Error: Latest datetime {latest_date} not found.")
                return pd.DataFrame()
        return pd.DataFrame()

    def get_latest_candle_datetime(self):
        latest_candle = self.get_latest_candle()
        if latest_candle is not None:
            return latest_candle.name
        return None

    def get_latest_candle_value(self, val):
        latest_candle = self.get_latest_candle()
        if latest_candle is not None and val in latest_candle:
            return latest_candle[val]
        return None

    def get_latest_candles_value(self, val, N=1):
        latest_candles = self.get_latest_candles(N)
        if not latest_candles.empty and val in latest_candles.columns:
            return latest_candles[val]
        return pd.Series(dtype=float)

    def visualize_data(self, val, y_label):
        fig, ax = plt.subplots(figsize=(14, 7))
        for symbol in self.symbols:
            if not self.data.empty and (val, symbol) in self.data.columns:
                ax.plot(self.data.index, self.data[(val, symbol)], label=symbol)
        ax.set_title(f"{y_label} vs Date")
        ax.set_xlabel("Date")
        ax.set_ylabel(y_label)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        plt.show()
        plt.close(fig)