import torch
from collections import deque

from src.Alpha9.market import events
from src.Alpha9.market.schemas import AbstractStrategy
from src.Alpha9.strategy.model import Model

class Strategy(AbstractStrategy):
    def __init__(self, data_handler, event_queue, model, symbols, seq_length, device):
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.model = model
        self.symbols = symbols
        self.seq_length = seq_length
        self.state_deque = deque(maxlen=seq_length)
        self.device = device

        self._candles_available = False

    def calculate_fiducia(self, event):
        print("Calculating fiducia...")
        if event.type == "MARKET":
            current_timestamp = event.timestamp
            candle = self.data_handler.get_latest_candle()
            self.state_deque.append(candle)
            if len(self.state_deque) < self.seq_length:
                return []
            torch.tensor(list(self.state_deque))
            # Passing it in the Model now.
            state_tensor = torch.tensor(self.state_deque)
            state_tensor = state_tensor.to(self.device)

            # Reshape the tensor to pass it in the model. Shape (1,SEQ_LENGTH, FEATURES)
            total_features = state_tensor.shape[1]
            model_input = state_tensor.reshape((1,self.seq_length,total_features))

            fiducia = Model.predict(model_input)
            fiducia = fiducia.reshape(-1)

            # Broadcast the signal event
            self.__broadcast_signal_event(current_timestamp, fiducia)



