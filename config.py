import json

import logger

class Config:
    def __init__(self):
        self.data = []
        self.name = ""

    def load_json(self, filename : str):
        self.name = filename

        self.data = json.load(open(filename, encoding="utf-8"))

        return True

    def save_json(self):
        with open(self.name, 'w', encoding="utf-8") as outfile:
            json.dump(self.data, outfile, indent=4, ensure_ascii=False)
            return True

        logger.fail_message("Can't save data in " + self.name)
        return False

    def get(self, key : str):
        return self.data[key]

    def has(self, key : str):
        return key in self.data

    def set_value(self, key : str, value):
        self.data[key] = value

    def print_data(self):
        print(self.data)