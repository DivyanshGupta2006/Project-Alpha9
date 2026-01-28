import talib as ta

def engineer(data,
             symbols,
             timeperiod_cat1,
             data_dir):
    for symbol in symbols:
        symbol = symbol.split('/')[0]
        featured_data = data[symbol]

        open_px = featured_data['open']
        high_px = featured_data['high']
        low_px = featured_data['low']
        close_px = featured_data['close']
        vol = featured_data['volume']

        # trend indicators
        featured_data['adx'] = ta.ADX(high_px, low_px, close_px, timeperiod=timeperiod_cat1)

        # momentum indicators


        # volatility indicators


        # volume indicators


        featured_data.dropna(inplace=True)
        featured_data.to_csv(data_dir / f'{symbol}.csv', index=True)
    return "Success"