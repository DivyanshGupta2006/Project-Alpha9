from market.schemas import AbstractRiskManager


class RiskManager(AbstractRiskManager):
    def __init__(self, data_handler, symbols, min_amt, stop_loss_multiple, stop_loss_fraction, take_profit_multiple,
                 take_profit_fraction):
        super().__init__()
        self.data_handler = data_handler
        self.symbols = symbols
        self._min_amt = min_amt
        self.stop_loss_multiple = stop_loss_multiple
        self.stop_loss_fraction = stop_loss_fraction
        self.take_profit_multiple = take_profit_multiple
        self.take_profit_fraction = take_profit_fraction

    def get_brackets(self, order_amount_and_order_price, portfolio):
        for symbol in self.symbols:
            amt = order_amount_and_order_price[symbol]['order-amt'] + portfolio[symbol]['amt']
            order_price = order_amount_and_order_price[symbol]['order-price']
            _natr = self.data_handler.get_latest_candle_value(('natr', symbol)) / 100
            sl_target = sl_amount = tp_target = tp_amount = 0

            if order_amount_and_order_price[symbol]['order-amt'] > self._min_amt:
                sl_target = order_price * (1 - self.stop_loss_multiple * _natr)
                sl_amount = amt * self.stop_loss_fraction
                tp_target = order_price * (1 + self.take_profit_multiple * _natr)
                tp_amount = amt * self.take_profit_fraction
            elif order_amount_and_order_price[symbol]['order-amt'] < -self._min_amt:
                sl_target = order_price * (1 + self.stop_loss_multiple * _natr)
                sl_amount = amt * self.stop_loss_fraction
                tp_target = order_price * (1 - self.take_profit_multiple * _natr)
                tp_amount = amt * self.take_profit_fraction

            order_amount_and_order_price[symbol]['stop-loss'] = {
                'price': sl_target,
                'portion': sl_amount
            }

            order_amount_and_order_price[symbol]['take-profit'] = {
                'price': tp_target,
                'portion': tp_amount
            }

    def check_brackets(self, portfolio):
        cash_delta = 0
        for symbol in self.symbols:
            low = self.data_handler.get_latest_candle_value(('low', symbol))
            high = self.data_handler.get_latest_candle_value(('high', symbol))
            if portfolio[symbol]['amt'] > self._min_amt:
                if low <= portfolio[symbol]['stop-loss']['price']:
                    cash_delta += portfolio[symbol]['stop-loss']['price'] * portfolio[symbol]['stop-loss']['portion']
                    portfolio[symbol]['amt'] -= portfolio[symbol]['stop-loss']['portion']
                    portfolio[symbol]['stop-loss']['portion'] = 0
                elif high >= portfolio[symbol]['take-profit']['price']:
                    cash_delta += portfolio[symbol]['take-profit']['price'] * portfolio[symbol]['take-profit']['portion']
                    portfolio[symbol]['amt'] -= portfolio[symbol]['take-profit']['portion']
                    portfolio[symbol]['take-profit']['portion'] = 0
            elif portfolio[symbol]['amt'] < -self._min_amt:
                if high >= portfolio[symbol]['stop-loss']['price']:
                    cash_delta += portfolio[symbol]['stop-loss']['price'] * portfolio[symbol]['stop-loss']['portion']
                    portfolio[symbol]['amt'] -= portfolio[symbol]['stop-loss']['portion']
                    portfolio[symbol]['stop-loss']['portion'] = 0
                elif low <= portfolio[symbol]['take-profit']['price']:
                    cash_delta += portfolio[symbol]['take-profit']['price'] * portfolio[symbol]['take-profit'][
                        'portion']
                    portfolio[symbol]['amt'] -= portfolio[symbol]['take-profit']['portion']
                    portfolio[symbol]['take-profit']['portion'] = 0

        return cash_delta