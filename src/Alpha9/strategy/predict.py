from src.Alpha9.market import schemas,events
from collections import deque
import torch
from src.Alpha9.strategy.model import Model

from src.Alpha9.market.events import MarketEvent
from src.Alpha9.pipeline.data_handler import DataHandler


class Strategy(schemas.AbstractStrategy):
    """
    This Strategy needs more documentation, we don't know how to describe this part. Hence, I will now leave this
    empty at the moment.
    """
    def __init__(self,event_queue,model,data_handler:DataHandler,symbols,seq_length):
        """
        Initialises the strategy.
        Parameters:
        events_queue - The events queue instance.
        data_handler - The data handler instance.
        symbols - A list of symbols traded by the strategy.
        seq_length - The length of the sequence to consider for each signal.
        """
        self.event_queue = event_queue
        self.data_handler = data_handler
        self.symbols = symbols
        self.seq_length = seq_length
        self.state_deque = deque(maxlen=seq_length)
        self.model = model
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        else :
            self.device = torch.device('cpu')

    def __broadcast_signal_event(self,timestamp,fiducia):
        event = events.SignalEvent(timestamp,fiducia)
        self.event_queue.put(event)

    def calculate_fiducia(self,event):
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








