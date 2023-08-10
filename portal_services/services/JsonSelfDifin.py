import os
import json
import threading


class JsonFile:
    def __init__(self, json_file):
        self.json_file = json_file

    def read_json(self):
        # 获取JSON文件的路径
        file_path = os.path.join(os.path.dirname(__file__), self.json_file)
        # 对文件加锁
        lock = threading.Lock()
        lock.acquire()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        finally:
            lock.release()
        return data

    def write_json(self, data):
        # 获取JSON文件的路径
        file_path = os.path.join(os.path.dirname(__file__), self.json_file)
        # 对文件加锁
        lock = threading.Lock()
        lock.acquire()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        finally:
            lock.release()

# 用例：
# user_info = JsonFile('user_pwd_tokens.json')
# data = user_info.read_json()
# user_info.write_json(data)
# 新建文件
