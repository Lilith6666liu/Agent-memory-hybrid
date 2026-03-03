import os
import requests
import json
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

# 从环境变量获取 Key
TEST_KEY = os.getenv("OPENAI_API_KEY")

url = "https://api.siliconflow.cn/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {TEST_KEY}",
    "Content-Type": "application/json"
}

# 我们特意换一个绝对不会下线、100% 免费的 7B 轻量级千问模型来做连通性测试
payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [{"role": "user", "content": "测试连接，请回复：收到"}],
    "max_tokens": 10
}

print("正在发送底层网络请求，获取真实诊断报告...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"\n【HTTP 状态码】: {response.status_code}")
    print(f"【服务器原始回复】: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ 彻底通了！模型可用！")
    else:
        print("\n❌ 拦截原因就在上面的【服务器原始回复】里！")
        
except Exception as e:
    print("❌ 网络彻底不通，原因:", e)