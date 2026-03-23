from Alpha9.market.events import OrderEvent

class Portfolio:
    def __init__(self, symbols, data_handler, risk_manager, start_date, initial_capital, bankrupt_fraction):
        self.symbols = symbols
        self.data_handler = data_handler
        self.risk_manager = risk_manager
        self.start_date = start_date
        self.initial_capital = float(initial_capital)

        self.current_portfolio = {}
        self.cash = self.initial_capital
        self.total_transaction_cost = 0.0

        self.all_portfolios = []
        self.bankrupt_threshold = initial_capital * bankrupt_fraction
        self.bankrupt = False

    def _record_portfolio(self, timestamp, total_equity):
        portfolio = {
            "timestamp": timestamp,
            "cash": self.cash,
            "total_equity": total_equity,
            "total_transaction_cost": self.total_transaction_cost,
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

        if total_value <= self.bankrupt_threshold:
            self.bankrupt = True
        return total_value

    def update_timeindex(self, event):
        if event.type == "MARKET":
            timestamp = event.timestamp
            total_value = self._calculate_portfolio_value()
            total_equity = total_value + self.cash
            self._record_portfolio(timestamp, total_equity)

    def _calculate_order_amount(self, event):
        order_amount = {}


        return order_amount

    def _generate_order(self, event):
        timestamp = event.timestamp
        order_amounts = self._calculate_order_amount(event)
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

        return order

    def update_signal(self, event):
        if event.type == "SIGNAL":
            return self._generate_order(event)
        else:
            return None

    def update_fill(self, event):
        if event.type == "FILL":
            timestamp = event.timestamp
            description = event.description
            cash_change = event.cash_change
            transaction_cost = event.transaction_cost

            self.cash += cash_change
            self.total_transaction_cost += transaction_cost

            for symbol in self.symbols:
                self.current_portfolio[symbol]=description["symbol"]