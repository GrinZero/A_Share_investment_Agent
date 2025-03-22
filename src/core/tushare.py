import tushare as ts
import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    print("环境变量文件不存在", env_path)

token = os.getenv('TUSHARE_TOKEN','')
ts.set_token(token=token)

tspro = ts.pro_api()