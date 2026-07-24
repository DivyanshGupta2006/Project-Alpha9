import torch

from Alpha9.market.events import SignalEvent
from Alpha9.market.schemas import AbstractStrategy


class Strategy(AbstractStrategy):
    def __init__(self, data_handler, event_queue, model, symbols, seq_length, device):
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.model = model
        self.symbols = symbols
        self.seq_length = seq_length
        self.device = device

        self._candles_available = False

    def calculate_fiducia(self, event):
        if event.type == "MARKET":
            current_timestamp = event.timestamp
            candles = self.data_handler.get_latest_candles(self.seq_length)
            if len(candles) < self.seq_length:
                return

            cols_drop = [
                col
                for col in candles.columns
                if col[0].lower() in ["open", "high", "low", "close", "volume"]
            ]
            candles = candles.drop(columns=cols_drop, errors="ignore")

            # Passing it in the Model now.
            state_tensor = torch.tensor(candles.values).to(self.device)

            # Reshape the tensor to pass it in the model. Shape (1,SEQ_LENGTH, FEATURES)
            model_input = state_tensor.reshape(
                (1, self.seq_length, state_tensor.shape[1])
            )

            fiducia = self.model.forward(model_input)
            fiducia = fiducia.reshape(-1)

            keys = self.symbols.copy()
            keys.append("EXPOSURE")
            fiducia_dict = dict(zip(keys, fiducia.tolist()))

            # Broadcast the signal event
            signal = SignalEvent(current_timestamp, fiducia_dict)
            self.event_queue.put_event(signal)
