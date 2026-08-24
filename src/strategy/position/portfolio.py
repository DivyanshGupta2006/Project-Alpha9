import pandas as pd
from market import schemas

class Portfolio(schemas.AbstractPortfolio):
    def __init__(self, symbols, data_handler, risk_manager, initial_capital, slippage_fraction, minimum_amount, bankruptcy_fraction):
        super().__init__()
        self.symbols = symbols
        self.data_handler = data_handler
        self.risk_manager = risk_manager
        self._capital = float(initial_capital)
        self._slippage_fraction = slippage_fraction
        self._min_amt = float(minimum_amount)
        self._bankruptcy_threshold = bankruptcy_fraction * initial_capital

        self._portfolio = {}
        for symbol in self.symbols:
            self._portfolio[symbol] = {
                'amt': 0.0,
                'avg-order-price': 0.0,
                'stop-loss': {
                    'price': 0.0,
                    'portion': 0.0
                },
                'take-profit': {
                    'price': 0.0,
                    'portion': 0.0
                }
            }

        self._cash = self._capital
        self._txn_cost = 0.0
        self._equity = self._cash
        self._portfolio_history = {}
        self._bankrupt = False

    def _record_holdings(self, timestamp):
        snapshot = {
            'portfolio': self._portfolio,
            'equity': self._equity,
            'cash': self._cash,
            'transaction cost': self._txn_cost,
        }
        self._portfolio_history[timestamp] = snapshot

    def _update_latest_equity(self):
        self.risk_manager.check_brackets(self._portfolio)

        sum = 0.0
        for symbol in self.symbols:
            amnt = self._portfolio[symbol]['amt']

            if abs(amnt) >= self._min_amt:
                latest_price = self.data_handler.get_latest_candle_value(('close', symbol))
                value = latest_price * amnt
                sum += value

        if sum <= self._bankruptcy_threshold:
            self._bankrupt = True

        self._equity = sum + self._cash

    def update_time_index(self, event):
        self._update_latest_equity()
        if self._bankrupt:
            self.data_handler.continue_backtest = False

        self._record_holdings(event.timestamp)

    def _get_order_amount_and_order_price(self, fiducia):
        res = {}
        for symbol in self.symbols:
            _close = self.data_handler.get_latest_candle_value(('close', symbol))
            amt_t1 = (self._equity * fiducia[symbol]) / _close
            amt_t0 = (self._portfolio[symbol]['amt'])
            order_amt = amt_t1 - amt_t0
            order_price = 0
            if order_amt > self._min_amt:
                order_price = _close * (1 + self._slippage_fraction)
            elif order_amt < -self._min_amt:
                order_price = _close * (1 - self._slippage_fraction)
            else:
                order_amt = 0

            res[symbol] = {
                'order-amt': order_amt,
                'order-price': order_price,
            }

        return res

    def update_signal(self, event):
        fiducia = event.fiducia
        order_amount_and_order_price = self._get_order_amount_and_order_price(fiducia)
        brackets = self.risk_manager.get_brackets()

    def update_fill(self, event):
        pass
    def save_equity(self):
        pass
    def visualize_equity(self):
        pass