import yaml

from src.Alpha9.utility import get_path

config_path = get_path.absolute('config.yaml')
with open(config_path, 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# OPTIMIZED
def load():
    return config

# OPTIMIZED
def refresh():
    global config
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)