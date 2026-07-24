import numpy as np

from Alpha9.market.events import FillEvent
from Alpha9.market.schemas import AbstractExchange


class Exchange(AbstractExchange):
    def __init__(self, event_queue, data_handler, transaction_cost_fraction, symbols):
        self.event_queue = event_queue
        self.data_handler = data_handler
        self.transaction_cost_fraction = transaction_cost_fraction
        self.symbols = symbols

    def execute_order(self, event):
        if event.type == "ORDER":
            desc = event.description
            cash_change = np.float64(0)
            transaction_cost = np.float64(0)
            for symbol in self.symbols:
                amt = desc[symbol]["amount"]
                if abs(amt) > 1e-8:
                    transaction_cost += abs(
                        amt * desc[symbol]["price"] * self.transaction_cost_fraction
                    )
                    cash_change -= amt * desc[symbol]["price"]
                    cash_change -= abs(
                        amt * desc[symbol]["price"] * self.transaction_cost_fraction
                    )

            fill_event = FillEvent(event.timestamp, desc, cash_change, transaction_cost)
            self.event_queue.put_event(fill_event)
