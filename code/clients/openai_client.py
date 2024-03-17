from openai import OpenAI
import os
from retry import retry

class OpenAiClient:
    def __init__(self,
                 model_name: str = "gpt-3.5-turbo",
        ) -> None:
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model_name

    @retry(tries=3, delay=1)
    def generate(self, message: str) -> str:
        try:
            completions = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": message}]
            )

            return completions.choices[0].message.content
        except Exception as e:
            print(f"Retrying LLM call {e}")
            raise Exception()