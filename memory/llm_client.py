"""
Unified LLM client supporting both chat completions and embeddings.
Compatible with OpenAI API and compatible providers (SiliconFlow, etc.)
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM operations: chat completions and embeddings."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
        self.model = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or .env file")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def call_llm_json(self, prompt: str, system: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call LLM and parse response as JSON."""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                return None
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
