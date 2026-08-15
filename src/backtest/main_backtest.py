from market.events import EventQueue
from src.backtest import performance_calculator as pf_calc

def backtest(data,
             start_date,
             end_date):

    event_queue = EventQueue()

    # TODO: Create a data handler using input above (remember to pass in the event_queue).


    while data.index < end_date: # temp while loop, should be something like data_handler.next_candle_exists
        # data_handler.update()
        while not event_queue.empty():
            event = event_queue.get_event()
            if event.type == "MARKET":
                # TODO: call function from predict.py script to get signal event
                pass
            elif event.type == "SIGNAL":
                # TODO: pass it in risk/portfolio manager to check for stop loss, and other factors like txn fees, slippage.
                pass
            elif event.type == "ORDER":
                # TODO: call execute.py script to execute order and get the final results.
                pass
            elif event.type == "FILL":
                # TODO: update portfolio manager with the fill event, to accurately calculate the portfolio.
                pass

    portfolio_history = 100
    pf_calc.calculate_performance(portfolio_history)
    return 1
