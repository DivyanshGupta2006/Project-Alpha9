import abc

class AbstractDataHandler(abc.ABC):
    @abc.abstractmethod
    def get_latest_candle(self):
        raise NotImplementedError("Should implement get_latest_candle()")

    @abc.abstractmethod
    def get_latest_candles(self, N=1):
        raise NotImplementedError("Should implement get_latest_candles()")

    @abc.abstractmethod
    def get_latest_candle_datetime(self):
        raise NotImplementedError("Should implement get_latest_candle_datetime()")

    @abc.abstractmethod
    def get_latest_candle_value(self, val):
        raise NotImplementedError("Should implement get_latest_candle_value()")

    @abc.abstractmethod
    def get_latest_candles_value(self, val, N=1):
        raise NotImplementedError("Should implement get_latest_candles_value()")

    @abc.abstractmethod
    def update_candles(self):
        raise NotImplementedError("Should implement update_candles()")

class AbstractStrategy(abc.ABC):
    @abc.abstractmethod
    def calculate_fiducia(self, event):
        raise NotImplementedError("Should implement calculate_fiducia()")

class AbstractPortfolio(abc.ABC):
    @abc.abstractmethod
    def update_timeindex(self, event):
        raise NotImplementedError("Should implement update_timeindex()")

    @abc.abstractmethod
    def update_signal(self, event):
        raise NotImplementedError("Should implement update_signal()")

    @abc.abstractmethod
    def update_fill(self, event):
        raise NotImplementedError("Should implement update_fill()")

class AbstractRiskManager(abc.ABC):
    @abc.abstractmethod
    def get_brackets(self, event):
        raise NotImplementedError("Should implement get_brackets()")

    @abc.abstractmethod
    def check_brackets(self, portfolio):
        raise NotImplementedError("Should implement check_brackets()")

class AbstractExchange(abc.ABC):
    @abc.abstractmethod
    def execute_order(self, event):
        raise NotImplementedError("Should implement execute_order()")