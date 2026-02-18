import requests
import json

API_BASE = 'http://127.0.0.1:8001'

print("测试 /api/stocks/scores?top_n=10")
print("=" * 50)
try:
    response = requests.get(f'{API_BASE}/api/stocks/scores?top_n=10', timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")

print("\n\n测试 /api/market/summary")
print("=" * 50)
try:
    response = requests.get(f'{API_BASE}/api/market/summary', timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")
