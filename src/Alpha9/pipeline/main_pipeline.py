from src.Alpha9.pipeline import feature_engineer
from src.Alpha9.utility import get_config, get_path, read_file

config = get_config.load()

def run():
    # load and handle paths
    raw_data_dir = get_path.absolute(config['path']['data']['raw'])
    featured_data_dir = get_path.absolute(config['path']['data']['featured'])
    get_path.check(raw_data_dir)
    get_path.check(featured_data_dir)

    # load and handle data downloading constants
    exchange = config['pipeline']['exchange']
    symbols = config['pipeline']['symbols']
    timeframe = config['pipeline']['timeframe']
    start_date = config['pipeline']['start_date']
    end_date = config['pipeline']['end_date']

    # load and handle feature engineering constants
    timeperiod_cat1 = config['pipeline']['timeperiod_cat1']

    # handle data downloading
    choice = input('Download the data [y/n] : ')
    if choice.lower() == 'y':
        from src.Alpha9.pipeline import download_data
        print("Please wait...\nThis may take a while...")
        status = download_data.download(exchange, symbols, timeframe, start_date, end_date, raw_data_dir)
        if status == 'Success':
            print('Successfully downloaded the data!')
        else:
            print(f'Failed to download the data : {status}')
            return status
    else:
        print("Using pre-downloaded data...")

    # handle feature engineering
    print("Creating features...")
    data = {}
    for symbol in symbols:
        symbol = symbol.split('/')[0]
        df = read_file.read_data('raw', symbol)
        data[symbol] = df
    status = feature_engineer.engineer(data, symbols, timeperiod_cat1, featured_data_dir)
    if status == 'Success':
        print('Successfully engineered the features!')
    else:
        print(f'Failed to engineer the features : {status}')
        return status

    return "Success"
