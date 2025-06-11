import openai
from dgf_prompt_generator import config

class LLMCaller:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=config.API_KEY,
            base_url=config.API_BASE_URL
        )
        self.model = config.MODEL_NAME
        self.temperature = config.TEMPERATURE

    def generate_code(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful C/C++ developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content
