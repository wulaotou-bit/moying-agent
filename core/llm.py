"""
墨影大模型调用封装
支持自动拼接长篇记忆、Token控制、异常处理、自动截断
"""
from openai import OpenAI
from config import Config
from utils.logger import log
import tiktoken
import openai

class LLMClient:
    def __init__(self, memory=None):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
            timeout=60
        )
        self.memory = memory  # 注入长篇记忆系统
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """计算Token数"""
        return len(self.encoding.encode(text))

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        调用大模型，自动拼接记忆
        :param system_prompt: 系统提示词
        :param user_prompt: 用户提示词
        :param temperature: 温度（0=严谨，1=创意）
        :param max_tokens: 最大输出Token
        :return: 模型输出
        """
        try:
            # 自动拼接长篇记忆（如果有记忆系统）
            if self.memory:
                relevant_memory = self.memory.query_relevant(user_prompt)
                all_characters = self.memory.get_all_characters()
                all_foreshadows = self.memory.get_all_foreshadows()
                
                # 截断过长的记忆（防止Token超限）
                while self.count_tokens(relevant_memory) > 1000:
                    relevant_memory = relevant_memory[:-100]
                
                full_system_prompt = f"""
                【长篇记忆】
                {relevant_memory}

                【强制遵守人设】
                {all_characters}

                【必须回收伏笔】
                {all_foreshadows}

                {system_prompt}
                """
            else:
                full_system_prompt = system_prompt

            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except openai.APITimeoutError:
            log.error("LLM调用超时")
            return "{}"
        except openai.APIError as e:
            log.error(f"LLM API错误: {str(e)}")
            return "{}"
        except Exception as e:
            log.error(f"LLM调用失败: {str(e)}")
            return "{}"