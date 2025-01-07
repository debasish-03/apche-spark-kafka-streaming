import yaml
import os


def __load_yaml__() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.yml')
    return yaml.safe_load(open(config_path))

def get(name: str) -> dict:
    yaml_file = __load_yaml__()
    return yaml_file[name]