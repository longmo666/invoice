#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 登录
response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
TOKEN = response.json()["data"]["access_token"]
headers = {"Authorization": f"Bearer {TOKEN}"}

# 测试配置 ID 4
config_id = 4

print("=== 测试连接 ===")
response = requests.post(f"{BASE_URL}/ai-configs/test-connection?config_id={config_id}", headers=headers)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

