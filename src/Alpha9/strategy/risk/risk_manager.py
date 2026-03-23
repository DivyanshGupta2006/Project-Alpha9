class RiskManager:
    def __init__(self, stop_loss_multiple, stop_loss_portion, take_profit_multiple, take_profit_portion, data_handler):
        self.stop_loss_multiple = stop_loss_multiple
        self.stop_loss_portion = stop_loss_portion
        self.take_profit_multiple = take_profit_multiple
        self.take_profit_portion = take_profit_portion
        self.data_handler = data_handler

    def calculate_order_prices(self, event):
        pass

    def calculate_order_brackets(self, event):
        pass