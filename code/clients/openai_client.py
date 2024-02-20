from openai import OpenAI
import os

class OpenAiClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.gptmodel = "gpt-3.5-turbo"
        self.userrole = "user"
        self.pre_prompt = "Give me information about the following, "

    def get_openai_response(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.gptmodel,
                messages=[
                    {"role": self.userrole, "content": self.pre_prompt + prompt}
                ]
            )

            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            return "I'm sorry, I couldn't complete your request."
