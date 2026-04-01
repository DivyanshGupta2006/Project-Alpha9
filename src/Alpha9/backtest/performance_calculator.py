import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")

class PerformanceCalculator:
    def __init__(self, equity_df, initial_capital, risk_free_rate):
        self.equity_df = equity_df.copy()
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.metrics = {}
        self.equity_df.index = pd.to_datetime(self.equity_df.index)
        self.equity_df.loc[:, 'daily_return'] = self.equity_df['total_equity'].pct_change()

    def calculate_metrics(self):
        pass

    def display_metrics(self):
        pass

    def generate_plots(self):
        pass