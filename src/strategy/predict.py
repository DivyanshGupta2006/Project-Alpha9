import torch

from market.events import SignalEvent
from market.schemas import AbstractStrategy


class Strategy(AbstractStrategy):
    def __init__(self, data_handler, model, symbols, seq_length, device):
        self.data_handler = data_handler
        self.model = model
        self.symbols = symbols.copy()
        self.symbols.append("EXPOSURE")
        self.seq_length = seq_length
        self.device = device

    def _normalize(self, x):
        return x

    def calculate_fiducia(self, event):
        current_timestamp = event.timestamp
        candles = self.data_handler.get_latest_candles(self.seq_length)
        if len(candles) < self.seq_length:
            return None

        cols_drop = [
            col
            for col in candles.columns
            if col[0].lower() in ["open", "high", "low", "close", "volume"]
        ]
        candles = candles.drop(columns=cols_drop, errors="ignore")

        state_tensor = torch.tensor(candles.values).to(self.device)

        model_input = self._normalize(state_tensor.reshape(
            (1, self.seq_length, state_tensor.shape[1])
        ))

        fiducia = self.model.forward(model_input)
        fiducia = self._sanitize(fiducia.reshape(-1))

        fiducia_dict = dict(zip(self.symbols, fiducia.tolist()))

        # Broadcast the signal event
        signal = SignalEvent(current_timestamp, fiducia_dict)
        return signal

    def _sanitize(self, fiducia):
        _sum = 0
        for val in fiducia:
            _sum += abs(val)
        return fiducia / _sum