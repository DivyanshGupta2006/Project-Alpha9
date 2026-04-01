class RiskManager:
    def __init__(self,
                 data_handler,
                 symbols,
                 slippage_cost_fraction,
                 stop_loss_multiple,
                 stop_loss_portion,
                 take_profit_multiple,
                 take_profit_portion):
        self.data_handler = data_handler
        self.symbols = symbols
        self.slippage_cost_fraction = slippage_cost_fraction
        self.stop_loss_multiple = stop_loss_multiple
        self.stop_loss_portion = stop_loss_portion
        self.take_profit_multiple = take_profit_multiple
        self.take_profit_portion = take_profit_portion

    def calculate_order_prices(self, event):
        order_prices = {}

        for symbol in self.symbols:
            # TODO: calculate slippage
            pass

        return order_prices

    def calculate_order_brackets(self, event):
        natr = self.data_handler.get_latest_candle_value('natr')
        close = self.data_handler.get_latest_candle_value('close')
        atr = natr * close / 100
        stop_loss_val = self.stop_loss_multiple * atr
        take_profit_val = self.take_profit_multiple * atr
        brackets = {
            'stop-loss': {},
            'take-profit': {}
        }
        for symbol in self.symbols:
            if abs(event.fiducia[symbol]) > 1e-9:
                # TODO: calculate stop-loss and take-profit
                pass
            else:
                brackets['stop-loss'][symbol] = {
                    'price': 0,
                    'portion': 0
                }
                brackets['take-profit'][symbol] = {
                    'price': 0,
                    'portion': 0
                }
        return brackets

