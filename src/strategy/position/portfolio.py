import copy
import pandas as pd

from market import schemas
from market.events import OrderEvent

class Portfolio(schemas.AbstractPortfolio):
    def __init__(self,
                 symbols,
                 data_handler,
                 risk_manager,
                 initial_capital,
                 slippage_fraction,
                 transaction_cost_fraction,
                 minimum_amount,
                 bankruptcy_fraction,
                 portfolio_dir):
        super().__init__()
        self.symbols = symbols
        self.data_handler = data_handler
        self.risk_manager = risk_manager
        self._capital = float(initial_capital)
        self._slippage_fraction = slippage_fraction
        self._transaction_cost_fraction = transaction_cost_fraction
        self._min_amt = float(minimum_amount)
        self._bankruptcy_threshold = bankruptcy_fraction * initial_capital
        self.portfolio_dir = portfolio_dir

        self._portfolio = {}
        for symbol in self.symbols:
            self._portfolio[symbol] = {
                'amt': 0.0,
                'avg-cost': 0.0,
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
        self._portfolio_history = []
        self._bankrupt = False

    def _record_holdings(self, timestamp):
        snapshot = {
            'timestamp': timestamp,
            'portfolio': copy.deepcopy(self._portfolio),
            'equity': self._equity,
            'cash': self._cash,
            'transaction cost': self._txn_cost,
        }
        self._portfolio_history.append(snapshot)

    def _update_latest_equity(self):
        sum = 0.0
        for symbol in self.symbols:
            amnt = self._portfolio[symbol]['amt']

            if abs(amnt) >= self._min_amt:
                latest_price = self.data_handler.get_latest_candle_value(('close', symbol))
                value = latest_price * amnt
                sum += value

        if sum + self._cash <= self._bankruptcy_threshold:
            self._bankrupt = True

        self._equity = sum + self._cash

    def update_time_index(self, event):
        cash_delta = self.risk_manager.check_brackets(self._portfolio)
        self._cash += cash_delta
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

            order_amt /= ((1 + self._transaction_cost_fraction) * (1 + self._slippage_fraction))

            res[symbol] = {
                'order-amt': order_amt,
                'order-price': order_price,
            }

        return res

    def update_signal(self, event):
        fiducia = event.fiducia
        order_amount_and_order_price = self._get_order_amount_and_order_price(fiducia)
        self.risk_manager.get_brackets(order_amount_and_order_price, self._portfolio)
        return OrderEvent(event.timestamp, order_amount_and_order_price)

    def _get_avg_cost_price(self, prev_avg_cost, prev_amt, order_price, order_amt):
        new_amt = prev_amt + order_amt
        new_avg_cost = prev_avg_cost
        same_dir_add = (
            prev_amt == 0 or (prev_amt > 0) == (order_amt > 0)
        )
        if abs(new_amt) < self._min_amt:
            return 0.0
        if same_dir_add:
            new_avg_cost = (prev_avg_cost * prev_amt + order_price * order_amt) / new_amt
        elif prev_amt != 0 and (prev_amt > 0) != (new_amt > 0):
            new_avg_cost = order_price
        return new_avg_cost

    def update_fill(self, event):
        self._cash += event.cash_delta
        self._txn_cost += event.txn_cost
        for symbol in self.symbols:
            if symbol in event.description:
                self._portfolio[symbol]['avg-cost'] = self._get_avg_cost_price(
                    self._portfolio[symbol]['avg-cost'],
                    self._portfolio[symbol]['amt'],
                    event.description[symbol]['order-price'],
                    event.description[symbol]['order-amt']
                )
                self._portfolio[symbol]['amt'] += event.description[symbol]['order-amt']
                self._portfolio[symbol]['stop-loss']['price'] = event.description[symbol]['stop-loss']['price']
                self._portfolio[symbol]['take-profit']['price'] = event.description[symbol]['take-profit']['price']
                self._portfolio[symbol]['stop-loss']['portion'] = event.description[symbol]['stop-loss']['portion']
                self._portfolio[symbol]['take-profit']['portion'] = event.description[symbol]['take-profit']['portion']

    def save_equity(self):
        rows = []
        for snapshot in self._portfolio_history:
            for symbol, pos in snapshot['portfolio'].items():
                rows.append({
                    'timestamp': snapshot['timestamp'],
                    'symbol': symbol,
                    'amt': f"{pos['amt']:.2f}",
                    'avg_cost': f"{pos['avg-cost']:.2f}",
                    'sl_price': f"{pos['stop-loss']['price']:.2f}",
                    'sl_portion': f"{pos['stop-loss']['portion']:.2f}",
                    'tp_price': f"{pos['take-profit']['price']:.2f}",
                    'tp_portion': f"{pos['take-profit']['portion']:.2f}",
                    'cash': f"{snapshot['cash']:.2f}",
                    'equity': f"{snapshot['equity']:.2f}",
                    'txn_cost': f"{snapshot['transaction cost']:.2f}",
                })

        pd.DataFrame(rows).to_csv(self.portfolio_dir / 'portfolio.csv', index=False)
    def visualize_equity(self):
        pass