import numpy as np

from market.schemas import AbstractPerformanceCalculator

class PerformanceCalculator(AbstractPerformanceCalculator):

    def __init__(self, initial_capital,  periods_per_year = 365*24):
        super().__init__()
        self.initial_capital = initial_capital
        self.period_per_year = periods_per_year

    def get_metrics(self, portfolio_history):
        if not portfolio_history or len(portfolio_history) < 3:
            return {}
        values = np.array([x['equity'] for x in portfolio_history], dtype=float)
        performance_metrics = {}
        annual_risk_free_rate = 0.03

        returns = np.diff(values) / values[:-1]

        running_max = np.maximum.accumulate(values)
        max_drawdown = float(np.max((running_max - values) / running_max))

        total_profit = values[-1] - values[0]
        cumulative_return = (values[-1] - values[0])/(values[0])


        # Sharpe Ratio
        returns = np.array(returns,dtype = np.float64)
        period_risk_free_rate = annual_risk_free_rate/self.period_per_year
        excess_returns = returns - period_risk_free_rate
        mean_excess_return = np.mean(excess_returns)
        std_dev = np.std(returns,ddof = 1)
        sharpe_ratio = (mean_excess_return/std_dev*np.sqrt(self.period_per_year)) if std_dev > 0 else 0

        # Sortino Ratio
        downside_diff = np.minimum(0, excess_returns)
        downside_std = np.sqrt(np.mean(downside_diff ** 2))
        sortino_ratio = (mean_excess_return / downside_std * np.sqrt(self.period_per_year)) if downside_std > 0 else 0.0

        txn_cost = portfolio_history[-1]['transaction cost']

        performance_metrics['total_profit'] = total_profit
        performance_metrics['cumulative_return'] = cumulative_return
        performance_metrics['max_drawdown'] = max_drawdown
        performance_metrics['sharpe_ratio'] = sharpe_ratio
        performance_metrics['sortino_ratio'] = sortino_ratio
        performance_metrics['transaction_cost'] = txn_cost

        return performance_metrics