import os
import pandas as pd

from Alpha9.utility import get_config, get_path

config = get_config.load()

def read_data(data_type, file):
    data_dir = get_path.absolute(config['path']['data'][data_type])
    file = f'{file.split('/')[0]}.csv'
    try:
        data = pd.read_csv(os.path.join(data_dir, file), index_col=0)
        data.index = pd.to_datetime(data.index)
        return data
    except Exception:
        return None