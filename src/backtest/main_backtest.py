import torch

from market.events import EventQueue
from pipeline.data_handler import DataHandler
from strategy.model import Model
from strategy.predict import Strategy
from strategy.risk.risk_manager import RiskManager
from strategy.position.portfolio import Portfolio
from market.exchange import Exchange
from backtest import performance_calculator as pf_calc, performance_calculator

from utility import get_config, get_path, read_file

config = get_config.load()

def run(data_type, start_date, end_date):

    if data_type == 'train':
        data = read_file.read_data('train', 'data')
    elif data_type == 'val':
        data = read_file.read_data('val', 'data')
    else:
        data = read_file.read_data('test', 'data')

    SYMBOLS = [s.split('/')[0] for s in config['pipeline']['symbols']]
    model_dir = get_path.absolute(config['path']['strategy']['model'])
    portfolio_dir = get_path.absolute(config['path']['strategy']['portfolio'])
    get_path.check(model_dir)
    get_path.check(portfolio_dir)
    seq_len = config['strategy']['sequence_length']
    min_amt = config['backtest']['minimum_amount']
    txn_cost = config['backtest']['transaction_cost_fraction']
    capital = config['backtest']['capital']
    bankruptcy_fraction = config['strategy']['bankruptcy_fraction']
    slippage = config['strategy']['slippage_cost_fraction']
    slm = config['strategy']['stop_loss_multiple']
    slp = config['strategy']['stop_loss_fraction']
    tpm = config['strategy']['take_profit_multiple']
    tpp = config['strategy']['take_profit_fraction']
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    market_updates = 0
    event_queue = EventQueue()
    data_handler = DataHandler(data, SYMBOLS, start_date, end_date, portfolio_dir)
    model = Model(SYMBOLS, model_dir)
    strategy = Strategy(data_handler, model, SYMBOLS, seq_len, device)
    risk_m = RiskManager(data_handler, SYMBOLS, min_amt, slm, slp, tpm, tpp)
    portfolio = Portfolio(SYMBOLS, data_handler, risk_m, capital, slippage, txn_cost, min_amt, bankruptcy_fraction, portfolio_dir)
    exchange = Exchange(SYMBOLS, txn_cost, min_amt)
    performance_calculator = pf_calc.PerformanceCalculator(capital)

    while data_handler.continue_backtest:
        event = data_handler.update_candles()
        if event:
            market_updates += 1
            event_queue.put_event(event)

            while not event_queue.empty():
                event = event_queue.get_event()

                if event.type == 'MARKET':
                    portfolio.update_time_index(event)
                    signal_event = strategy.calculate_fiducia(event)
                    if signal_event:
                        event_queue.put_event(signal_event)

                elif event.type == 'SIGNAL':
                    order_event = portfolio.update_signal(event)
                    if order_event:
                        event_queue.put_event(order_event)

                elif event.type == 'ORDER':
                    fill_event = exchange.execute_order(event)
                    if fill_event:
                        event_queue.put_event(fill_event)

                elif event.type == 'FILL':
                    portfolio.update_fill(event)


    portfolio.save_equity()
    portfolio.visualize_equity()
    metrics = performance_calculator.get_metrics(portfolio._portfolio_history)
    for symbol in SYMBOLS:
        data_handler.plot_value(('close', symbol))
    print(metrics)