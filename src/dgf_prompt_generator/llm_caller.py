import logging
import os
from importlib import import_module
from typing import Any

import openai

LOGGER = logging.getLogger(__name__)

local_config: Any = None
try:
    # Backward-compatible local private config.
    local_config = import_module("dgf_prompt_generator.config")
except Exception:  # pragma: no cover - optional local module
    pass

class LLMCaller:
    def __init__(self, api_key=None, base_url=None, model=None, temperature=None):
        final_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("DGF_API_KEY")
        if not final_api_key and local_config is not None:
            final_api_key = getattr(local_config, "API_KEY", None)

        if not final_api_key:
            raise ValueError(
                "Missing OpenAI API key. Set OPENAI_API_KEY (or DGF_API_KEY), "
                "or provide dgf_prompt_generator/config.py."
            )

        final_base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("DGF_API_BASE_URL")
        if not final_base_url and local_config is not None:
            final_base_url = getattr(local_config, "API_BASE_URL", None)

        final_model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        if (not model) and local_config is not None:
            final_model = getattr(local_config, "MODEL_NAME", final_model)

        final_temperature = temperature
        if final_temperature is None:
            final_temperature = os.getenv("OPENAI_TEMPERATURE", "0.2")
        if local_config is not None and temperature is None:
            final_temperature = getattr(local_config, "TEMPERATURE", final_temperature)
        try:
            final_temperature = float(final_temperature)
        except (TypeError, ValueError):
            LOGGER.warning("Invalid OPENAI_TEMPERATURE=%r, fallback to 0.2", final_temperature)
            final_temperature = 0.2

        self.client = openai.OpenAI(
            api_key=final_api_key,
            base_url=final_base_url
        )
        self.model = final_model
        self.temperature = final_temperature

    def generate_code(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful C/C++ developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        LOGGER.debug("LLM generation finished using model=%s", self.model)
        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("LLM response has no choices.")
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response has empty content.")
        return content
