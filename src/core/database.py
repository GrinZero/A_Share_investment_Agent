import os
from pymongo import MongoClient
import atexit
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    print("环境变量文件不存在", env_path)

MONGODB_URI = os.getenv('MONGODB_URI','mongodb://root:example@localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE','investment_agent')

mongo_client = MongoClient(MONGODB_URI)


def cleanup():
    if mongo_client:
        mongo_client.close()

atexit.register(cleanup)