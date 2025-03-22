import os
from pymongo import MongoClient
import atexit

mongo_client = MongoClient("mongodb://root:example@localhost:27017/")


def cleanup():
    if mongo_client:
        mongo_client.close()

atexit.register(cleanup)