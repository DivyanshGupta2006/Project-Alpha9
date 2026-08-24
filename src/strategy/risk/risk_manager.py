from market.schemas import AbstractRiskManager

class RiskManager(AbstractRiskManager):
    def __init__(self):
        super().__init__()

    def get_brackets(self, event):
        pass

    def check_brackets(self, event):
        pass