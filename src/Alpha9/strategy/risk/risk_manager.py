class RiskManager:
    def __init__(
        self,
        data_handler,
        symbols,
        slippage_cost_fraction,
        stop_loss_multiple,
        stop_loss_portion,
        take_profit_multiple,
        take_profit_portion,
    ):
        self.data_handler = data_handler
        self.symbols = symbols
        self.slippage_cost_fraction = slippage_cost_fraction
        self.stop_loss_multiple = stop_loss_multiple
        self.stop_loss_portion = stop_loss_portion
        self.take_profit_multiple = take_profit_multiple
        self.take_profit_portion = take_profit_portion

    def calculate_order_info(self, event, pvalue, portfolio):
        order_info = {}

        if event.type == "SIGNAL":
            for symbol in self.symbols:
                order_info[symbol] = {}
                invested = pvalue * event.fiducia[symbol]
                close = self.data_handler.get_latest_candle_value(("close", symbol))
                order_info[symbol]["amount"] = invested / close
                order_info[symbol]["order_amount"] = (
                    order_info[symbol]["amount"] - portfolio[symbol]["amount"]
                )

                if abs(order_info[symbol]["order_amount"]) > 1e-8:
                    if order_info[symbol]["order_amount"] > 0:
                        order_info[symbol]["price"] = close * (
                            1 + self.slippage_cost_fraction
                        )
                    else:
                        order_info[symbol]["price"] = close * (
                            1 - self.slippage_cost_fraction
                        )
                else:
                    order_info[symbol]["price"] = 0

        return order_info

    def calculate_order_brackets(self, order_info):
        brackets = {"stop-loss": {}, "take-profit": {}}
        for symbol in self.symbols:
            order_price = order_info[symbol]["price"]
            order_amount = order_info[symbol]["order_amount"]
            final_amount = order_info[symbol]["amount"]
            natr = self.data_handler.get_latest_candle_value(("natr", symbol))
            close = self.data_handler.get_latest_candle_value(("close", symbol))
            atr = natr * close / 100
            stop_loss_val = self.stop_loss_multiple * atr
            take_profit_val = self.take_profit_multiple * atr
            if abs(order_amount) > 1e-8:
                if (
                    final_amount > 0
                ):  # decided on basis of whether final amount is positive or negative - whether or not finally we are in a long or short position
                    brackets["stop-loss"][symbol] = {
                        "price": order_price - stop_loss_val,
                        "portion": self.stop_loss_portion * final_amount,
                    }
                    brackets["take-profit"][symbol] = {
                        "price": order_price + take_profit_val,
                        "portion": self.take_profit_portion * final_amount,
                    }
                else:
                    brackets["stop-loss"][symbol] = {
                        "price": order_price + stop_loss_val,
                        "portion": self.stop_loss_portion
                        * final_amount,  # portion is negative !!
                    }
                    brackets["take-profit"][symbol] = {
                        "price": order_price - take_profit_val,
                        "portion": self.take_profit_portion
                        * final_amount,  # portion is negative !!
                    }
            else:
                brackets["stop-loss"][symbol] = {"price": 0, "portion": 0}
                brackets["take-profit"][symbol] = {"price": 0, "portion": 0}
        return brackets
