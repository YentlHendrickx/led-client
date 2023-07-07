# Author: Yentl Hendrickx
# Last modified: 2023-07-07
# Description: Config handler, adds, reads and removes from config file

import json


class ConfigHandler:
    def __init__(self, config_file):
        self.config_file = config_file

    def add_config(self, config_dict):
        try:
            with open(self.config_file, 'r') as file:
                existing_config = json.load(file)
        except FileNotFoundError:
            existing_config = {}

        existing_config.update(config_dict)

        with open(self.config_file, 'w') as file:
            json.dump(existing_config, file)

    def remove_config(self, config_key):
        try:
            with open(self.config_file, 'r') as file:
                existing_config = json.load(file)
        except FileNotFoundError:
            return

        existing_config.pop(config_key, None)

        with open(self.config_file, 'w') as file:
            json.dump(existing_config, file)

    def get_config(self, config_key):
        try:
            with open(self.config_file, 'r') as file:
                existing_config = json.load(file)
        except FileNotFoundError:
            return "Config file not found.", None

        value = existing_config.get(config_key, None)
        if value is None:
            return "Key not found.", None

        return value
