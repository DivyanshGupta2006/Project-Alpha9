from Alpha9.pipeline import feature_engineer, merge_split_data
from Alpha9.utility import get_config, get_path, read_file

config = get_config.load()

def run():
    # load and handle paths
    raw_data_dir = get_path.absolute(config['path']['data']['raw'])
    featured_data_dir = get_path.absolute(config['path']['data']['featured'])
    train_data_dir = get_path.absolute(config['path']['data']['train'])
    val_data_dir = get_path.absolute(config['path']['data']['val'])
    test_data_dir = get_path.absolute(config['path']['data']['test'])
    get_path.check(raw_data_dir)
    get_path.check(featured_data_dir)
    get_path.check(train_data_dir)
    get_path.check(val_data_dir)
    get_path.check(test_data_dir)

    # load and handle data downloading constants
    exchange = config['pipeline']['exchange']
    symbols = config['pipeline']['symbols']
    timeframe = config['pipeline']['timeframe']
    start_date = config['pipeline']['start_date']
    end_date = config['pipeline']['end_date']

    # load and handle feature engineering constants
    timeperiod_cat = config['pipeline']['timeperiod_cat']
    timeperiod_cat0 = config['pipeline']['timeperiod_cat0']
    timeperiod_cat1 = config['pipeline']['timeperiod_cat1']
    timeperiod_cat2 = config['pipeline']['timeperiod_cat2']
    timeperiod_cat3 = config['pipeline']['timeperiod_cat3']
    timeperiod_cat4 = config['pipeline']['timeperiod_cat4']
    selected_features = config['pipeline']['selected_features']

    # load and handle merge and split constants
    train_start_date = config['pipeline']['train_start_date']
    val_start_date = config['pipeline']['val_start_date']
    test_start_date = config['pipeline']['test_start_date']

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
    symbols = [symbol.split('/')[0] for symbol in symbols]
    for symbol in symbols:
        df = read_file.read_data('raw', symbol)
        data[symbol] = df
    status = feature_engineer.engineer(data, symbols, timeperiod_cat, timeperiod_cat0, timeperiod_cat1, timeperiod_cat2, timeperiod_cat3, timeperiod_cat4, selected_features, featured_data_dir)
    if status == 'Success':
        print('Successfully engineered the features!')
    else:
        print(f'Failed to engineer the features : {status}')
        return status

    # handle merge & split
    print("Performing Merge & Split")
    data = {}
    for symbol in symbols:
        df = read_file.read_data('featured', symbol)
        data[symbol] = df
    status = merge_split_data.merge_split(data, symbols, train_start_date, val_start_date, test_start_date, train_data_dir, val_data_dir, test_data_dir)
    if status == 'Success':
        print('Successfully performed merge & split!')
    else:
        print(f'Failed to perform merge & split : {status}')
        return status

    return "Success"
