"""
Optional local configuration for LLM caller.
Prefer environment variables in production:
  - OPENAI_API_KEY
  - OPENAI_BASE_URL (optional)
  - OPENAI_MODEL (optional)
  - OPENAI_TEMPERATURE (optional)
"""

API_KEY = "replace-with-your-api-key"
API_BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0.2
