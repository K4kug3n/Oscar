from pymongo import MongoClient

class Database:
    def __init__(self, link : str, cluster : str):
       self.db = MongoClient(link)[cluster]

    def get_all(self, collection : str):
        return self.db[collection].find()

    def get_one(self, collection : str, filter : dict):
        return self.db[collection].find_one(filter)

    def replace_one(self, collection : str, filter : dict, value : dict):
        result = self.db[collection].replace_one(filter, value)

        return (result.matched_count == 1)

    def delete_one(self, collection : str, filter : dict):
        self.db[collection].delete_one(filter)

    def insert_one(self, collection : str, data : dict):
        self.db[collection].insert_one(data)

