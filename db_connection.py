from pymongo import MongoClient
from config import MONGO_URI

def get_mongo_client():
    return MongoClient(MONGO_URI)

def get_reviews_collection():
    client = get_mongo_client()
    db = client["Solar"]
    return db['Reviews']

def get_solar_info_collection():
    client = get_mongo_client()
    db = client["Solar"]
    return db['SolarInfo']