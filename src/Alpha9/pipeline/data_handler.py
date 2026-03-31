from src.Alpha9.market.schemas import AbstractDataHandler


class DataHandler(AbstractDataHandler):
    def __init__(self,symbols):
        self.data = None
        self.timestamp = 0
        self.symbols = symbols

    def get_latest_candle(self):
        pass
    def get_latest_candles(self, N=1):
        pass
    def get_latest_candle_datetime(self):
        pass
    def get_latest_candle_value(self, val):
        pass
    def get_latest_candles_value(self, val, N=1):
        pass
    def update_candles(self):
        self.timestamp += 1