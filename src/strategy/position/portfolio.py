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

    def update_fill(self, event):
        self._cash += event.cash_delta
        self._txn_cost += event.txn_cost
        for symbol in self.symbols:
            if symbol in event.description:

                self._portfolio[symbol]['avg-cost'] = (
                        (self._portfolio[symbol]['avg-cost'] * self._portfolio[symbol]['amt']
                         + event.description[symbol]['order-price'] * event.description[symbol]['order-amt'])
                        / (self._portfolio[symbol]['amt'] + event.description[symbol]['order-amt']))
                self._portfolio[symbol]['amt'] += event.description[symbol]['order-amt']
                self._portfolio[symbol]['stop-loss']['price'] = event.description[symbol]['stop-loss']['price']
                self._portfolio[symbol]['take-profit']['price'] = event.description[symbol]['take-profit']['price']
                self._portfolio[symbol]['stop-loss']['portion'] = event.description[symbol]['stop-loss']['portion']
                self._portfolio[symbol]['take-profit']['portion'] = event.description[symbol]['take-profit']['portion']

    def save_equity(self):
        # rows = []
        # for snapshot in self._portfolio_history:
        #     for symbol, pos in snapshot['portfolio'].items():
        #         rows.append({
        #             'timestamp': snapshot['timestamp'],
        #             'symbol': symbol,
        #             'amt': pos['amt'],
        #             'avg_cost': pos['avg-cost'],
        #             'sl_price': pos['stop-loss']['price'],
        #             'sl_portion': pos['stop-loss']['portion'],
        #             'tp_price': pos['take-profit']['price'],
        #             'tp_portion': pos['take-profit']['portion'],
        #             'cash': snapshot['cash'],
        #             'equity': snapshot['equity'],
        #             'txn_cost': snapshot['transaction cost'],
        #         })

        pd.DataFrame(self._portfolio_history).to_csv(self.portfolio_dir / 'portfolio.csv', index=False)
    def visualize_equity(self):
        pass