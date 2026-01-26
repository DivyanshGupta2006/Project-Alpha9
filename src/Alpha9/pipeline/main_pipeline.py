from src.Alpha9.utility import get_config, get_path

config = get_config.load()

def run():
    # load and handle paths
    raw_data_dir = get_path.absolute(config['path']['data']['raw'])
    get_path.check(raw_data_dir)

    # load and handle other constants
    exchange = config['pipeline']['exchange']
    symbols = config['pipeline']['symbols']
    timeframe = config['pipeline']['timeframe']
    start_date = config['pipeline']['start_date']
    end_date = config['pipeline']['end_date']

    choice = input('Download the data [y/n] : ')
    if choice.lower() == 'y':
        from src.Alpha9.pipeline import download_data
        print("Please wait...\nThis may take a while...")
        status = download_data.download(exchange, symbols, timeframe, start_date, end_date, raw_data_dir)
        if status == 'Success':
            print('Successfully downloaded the data!')
        else:
            print(f'Failed to download the data : {status}')
