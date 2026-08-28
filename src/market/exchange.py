import copy

from market.schemas import AbstractExchange
from market.events import FillEvent

class Exchange(AbstractExchange):
    def __init__(self, symbols, transaction_cost_fraction, min_amt):
        super().__init__()
        self.symbols = symbols
        self._transaction_cost_fraction = transaction_cost_fraction
        self._min_amt = min_amt

    def execute_order(self, event):
        desc = event.description
        fills = {}
        cash_delta = 0
        transaction_cost = 0
        for symbol in self.symbols:
            amt = desc[symbol]['order-amt']
            price = desc[symbol]['order-price']

            order_val = amt * price
            transaction_cost += self._transaction_cost_fraction * abs(order_val)
            cash_delta -= (order_val)
            fills[symbol] = copy.deepcopy(desc[symbol])

        cash_delta -= transaction_cost

        return FillEvent(event.timestamp, fills, cash_delta, transaction_cost)