import yaml

from utility import get_path

config_path = get_path.absolute('config.yaml')
with open(config_path, 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

def load():
    return config

def refresh():
    global config
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)