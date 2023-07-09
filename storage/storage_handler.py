# Author: Yentl Hendrickx
# Last modified: 2023-07-09
# Description: Storage handler, adds, reads and removes from storage file

import json


class StorageHandler:
    def __init__(self, source_file):
        self.source_file = source_file

    def add_value(self, source_dict):
        try:
            with open(self.source_file, 'r') as file:
                existing_file = json.load(file)
        except FileNotFoundError:
            existing_file = {}

        existing_file.update(source_dict)

        with open(self.source_file, 'w') as file:
            json.dump(existing_file, file)

    def remove_value(self, source_key):
        try:
            with open(self.source_file, 'r') as file:
                existing_file = json.load(file)
        except FileNotFoundError:
            return

        existing_file.pop(source_key, None)

        with open(self.source_file, 'w') as file:
            json.dump(existing_file, file)

    def get_value(self, source_key):
        try:
            with open(self.source_file, 'r') as file:
                existing_file = json.load(file)
        except FileNotFoundError:
            return "Source file not found.", None

        value = existing_file.get(source_key, None)
        if value is None:
            return "Key not found.", None

        return value
