from pymongo import MongoClient

def connect_mongo_db():
    client = MongoClient("mongodb+srv://michael:7fH9B9EDaPzyp0GK@datahub-dev.wfo6j.mongodb.net/datahub?retryWrites=true&w=majority")
    return client.datahub