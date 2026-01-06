import ccxt
import time
import pandas as pd

# OPTIMIZED
def download(exchange,
             symbols,
             timeframe,
             start_date,
             end_date,
             data_dir):
    try:
        exchange = getattr(ccxt, exchange)()
    except Exception as e:
        return str(e)

    for symbol in symbols:
        fetched_data_list = []

        start = exchange.parse8601(start_date + 'T00:00:00Z')
        end = exchange.parse8601(end_date + 'T23:59:59Z')
        while start < end:
            try:
                fetched_data_point = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=start)
                if not fetched_data_point:
                    return "Unexpected Error"
                fetched_data_list.extend(fetched_data_point)
                start = fetched_data_point[-1][0] + 1
                time.sleep(exchange.rateLimit / 1000)
            except Exception as e:
                return str(e)

        fetched_data_list = [candle for candle in fetched_data_list if candle[0] <= end]

        fetched_data_dataframe = pd.DataFrame(fetched_data_list,
                                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        fetched_data_dataframe['timestamp'] = pd.to_datetime(fetched_data_dataframe['timestamp'], unit='ms')
        fetched_data_dataframe.to_csv(data_dir / f'{symbol.split('/')[0]}.csv', index=False)

    return "Success"
