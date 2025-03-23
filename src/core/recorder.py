
import os
from dotenv import load_dotenv
import queue
import threading
import json
import requests
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    print("环境变量文件不存在", env_path)

webhook_url = os.getenv('N8N_WEBHOOK_URL','')

# 使用线程安全的队列存储记录
record_queue = queue.Queue()

# 当前批次的记录
current_record = {
    "order_record": [],
    "log_record": []
}

# 线程锁，用于同步对 current_record 的访问
record_lock = threading.Lock()

def add_order_record(order_data):
    """添加订单记录到队列"""
    record_queue.put(("order", order_data))

def add_log_record(log_data):
    """添加日志记录到队列"""
    record_queue.put(("log", log_data))

def process_record_queue():
    """处理队列中的记录，更新到当前批次"""
    global current_record
    
    # 处理队列中所有可用的记录
    while not record_queue.empty():
        try:
            record_type, data = record_queue.get_nowait()
            with record_lock:
                if record_type == "order":
                    current_record["order_record"].append(data)
                elif record_type == "log":
                    current_record["log_record"].append(data)
            record_queue.task_done()
        except queue.Empty:
            break

def send_record():
    """发送当前批次的记录"""
    global current_record, webhook_url
    
    # 先处理队列中的所有记录
    process_record_queue()
    
    print('发送记录',current_record)
    # 检查是否有记录需要发送
    with record_lock:
        if not current_record['order_record'] and not current_record['log_record']:
            return None
        
        # 复制当前记录用于发送
        record_to_send = {
            "order_record": current_record["order_record"].copy(),
            "log_record": current_record["log_record"].copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    # 发送记录
    if webhook_url:
        try:
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(record_to_send)
            response = requests.post(webhook_url, headers=headers, data=data)
            if response.status_code != 200:
                print(f"发送记录失败: {response.status_code} {response.text}")
        except Exception as e:
            print(f"发送记录异常: {str(e)}")
    
    return record_to_send

def reset_record():
    """重置当前批次的记录"""
    global current_record
    
    # 先处理队列中的所有记录
    process_record_queue()
    
    # 重置当前记录
    with record_lock:
        current_record = {
            "order_record": [],
            "log_record": []
        }
    
    return current_record