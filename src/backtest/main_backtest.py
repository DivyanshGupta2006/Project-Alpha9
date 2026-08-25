import torch

from market.events import EventQueue
from pipeline.data_handler import DataHandler
from strategy.model import Model
from strategy.predict import Strategy
from strategy.risk.risk_manager import RiskManager
from strategy.position.portfolio import Portfolio
from market.exchange import Exchange
from backtest import performance_calculator as pf_calc

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
    seq_len = 2
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
    data_handler = DataHandler(data, SYMBOLS, start_date, end_date)
    model = Model(SYMBOLS, model_dir)
    strategy = Strategy(data_handler, model, SYMBOLS, seq_len, device)
    risk_m = RiskManager(data_handler, SYMBOLS, min_amt, slm, slp, tpm, tpp)
    portfolio = Portfolio(SYMBOLS, data_handler, risk_m, capital, slippage, txn_cost, min_amt, bankruptcy_fraction, portfolio_dir)
    exchange = Exchange(SYMBOLS, txn_cost, min_amt)

    while data_handler.continue_backtest:
        event = data_handler.update_candles()
        if event:
            market_updates += 1
            event_queue.put_event(event)

            while not event_queue.empty():
                event = event_queue.get_event()
                print(event)

                if event.type == 'MARKET':
                    print(event.timestamp)
                    portfolio.update_time_index(event)
                    print(portfolio._portfolio)
                    print(portfolio._portfolio_history)
                    signal_event = strategy.calculate_fiducia(event)
                    if signal_event:
                        event_queue.put_event(signal_event)

                elif event.type == 'SIGNAL':
                    print(event.fiducia)
                    order_event = portfolio.update_signal(event)
                    if order_event:
                        event_queue.put_event(order_event)

                elif event.type == 'ORDER':
                    print(event.description)
                    fill_event = exchange.execute_order(event)
                    if fill_event:
                        event_queue.put_event(fill_event)

                elif event.type == 'FILL':
                    print(event.description)
                    print(event.cash_delta)
                    print(event.txn_cost)
                    portfolio.update_fill(event)


    portfolio.save_equity()
    print(market_updates)


run('train', '2021-01-01 00:00:00', '2021-01-01 09:00:00')