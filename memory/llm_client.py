import os
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 环境变量
# 尝试加载当前目录和父目录下的 .env 文件
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv(override=True)  # 也尝试加载当前运行目录下的 .env

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    """
    轻量级 LLM 客户端，用于调用大模型进行 JSON 格式的结构化输出。
    """
    def __init__(self):
        # 从环境变量获取 API 配置
        # 注意：SiliconFlow 的 base_url 应该是 https://api.siliconflow.cn/v1
        # OpenAI SDK 会自动在后面拼接 /chat/completions
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
        self.model = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY，请确保已在环境变量或 .env 文件中设置。")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def call_llm_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 并强制要求返回 JSON 格式。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM 调用或解析失败: {str(e)}")
            return None
