import openai
import config

class LLMCaller:
    def __init__(self):
        self.api_key = config.API_KEY
        self.api_base = config.API_BASE_URL
        self.model = config.MODEL_NAME
        self.temperature = config.TEMPERATURE

        openai.api_key = self.api_key
        openai.api_base = self.api_base

    def generate_code(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful C/C+++ developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        return response['choices'][0]['message']['content']
