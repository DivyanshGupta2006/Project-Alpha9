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
        pass

    def calculate_order_brackets(self, event):
        natr = self.data_handler.get_latest_candle_value('natr')
        close = self.data_handler.get_latest_candle_value('close')
        brackets = {
            'stop-loss': {},
            'take-profit': {}
        }
        for symbol in self.symbols:
            if event.fiducia[symbol] != 0:
                atr = (natr[symbol] * close[symbol]) / 100
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

