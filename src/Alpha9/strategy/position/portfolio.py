import pandas as pd

from Alpha9.market.events import OrderEvent

class Portfolio:
    def __init__(self, symbols, data_handler, event_queue, risk_manager, start_date, initial_capital, bankrupt_fraction, equity_data_path):
        self.symbols = symbols
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.risk_manager = risk_manager
        self.start_date = start_date
        self.initial_capital = float(initial_capital)
        self.equity_data_path = equity_data_path

        self.current_portfolio = {}
        for symbol in self.symbols:
            self.current_portfolio[symbol] = {
                'amount': 0,
                'cost-basis': 0,
                'stop-loss': {
                    'price': 0,
                    'portion': 0
                },
                'take-profit': {
                    'price': 0,
                    'portion': 0
                }
            }
        self.cash = self.initial_capital
        self.total_transaction_cost = 0.0
        self.all_portfolios = []
        self.bankrupt_threshold = initial_capital * bankrupt_fraction
        self.bankrupt = False

        self._record_portfolio(pd.Timestamp(self.start_date), self._calculate_portfolio_value())

    def _record_portfolio(self, timestamp, total_equity):
        portfolio = {
            "timestamp": timestamp,
            "cash": self.cash,
            "tota-equity": total_equity,
            "total-transaction-cost": self.total_transaction_cost,
            "portfolio": self.current_portfolio,
        }
        self.all_portfolios.append(portfolio)

    def _calculate_portfolio_value(self):
        total_value = 0.0
        for symbol in self.symbols:
            current = self.current_portfolio[symbol]
            amount = current["amount"]

            if amount != 0:
                latest_price = self.data_handler.get_latest_candle_value('close')
                value = amount * latest_price
                total_value += value

        if total_value <= self.bankrupt_threshold or self.cash < 0:
            self.bankrupt = True
        return total_value

    def update_timeindex(self, event):
        if event.type == "MARKET":
            timestamp = event.timestamp
            for symbol in self.symbols:
                # TODO: Check for stop-loss and take profit
                pass
            total_value = self._calculate_portfolio_value()
            total_equity = total_value + self.cash
            self._record_portfolio(timestamp, total_equity)

    def _sanitize(self, event):
        order_amount = {}

        for symbol in self.symbols:
            # TODO: calculate order amounts
            pass

        return order_amount

    def update_signal(self, event):
        if event.type == "SIGNAL":
            timestamp = event.timestamp
            order_amounts = self._sanitize(event)
            description = {}

            order_prices = self.risk_manager.calculate_order_prices(event)
            brackets = self.risk_manager.calculate_order_brackets(event)

            for symbol in self.symbols:
                description[symbol] = {
                    "timestamp": timestamp,
                    "amount": order_amounts[symbol],
                    "price": order_prices[symbol],
                    "stop-loss": brackets['stop loss'][symbol],
                    "take-profit": brackets['take profit'][symbol]
                }
            order = OrderEvent(timestamp, description)
            self.event_queue.put_event(order)
        else:
            return None

    def update_fill(self, event):
        if event.type == "FILL":
            description = event.description
            cash_change = event.cash_change
            transaction_cost = event.transaction_cost

            self.cash += cash_change
            self.total_transaction_cost += transaction_cost

            for symbol in self.symbols:
                portfolio_ = description[symbol]
                if abs(portfolio_["amount"]) < 1e-9:
                    portfolio_["amount"] = 0
                self.current_portfolio[symbol]["amount"] += portfolio_["amount"]
                self.current_portfolio[symbol]["stop-loss"] = portfolio_["stop-loss"]
                self.current_portfolio[symbol]["take-profit"] = portfolio_["take-profit"]

    def save_equity_data(self):
        df = pd.DataFrame(self.all_portfolios)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = df[~df.index.duplicated(keep='last')]
        df.sort_index(inplace=True)
        df.to_csv(self.equity_data_path, index=True)