
import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    print("环境变量文件不存在", env_path)

webhook_url = os.getenv('N8N_WEBHOOK_URL','')

record = {
    "order_record": [],
    "log_record": []
}

def send_record():
    global record, webhook_url
    # fetch webhook_url
    if webhook_url == '':
        return
    # make sure data is not empty
    if record['order_record'] == []:
        return

    import requests
    import json
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps(record)
    response = requests.post(webhook_url, headers=headers, data=data)
    # send record to n8n

    return record

def reset_record():
    global record
    record = {
        "order_record": [],
        "log_record": []
    }
    return record