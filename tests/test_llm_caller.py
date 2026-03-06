from types import SimpleNamespace

import pytest

from dgf_prompt_generator import llm_caller
from dgf_prompt_generator.llm_caller import LLMCaller


def test_llm_caller_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DGF_API_KEY", raising=False)
    monkeypatch.setattr(llm_caller, "local_config", None)
    with pytest.raises(ValueError):
        LLMCaller()


def test_llm_caller_generate_code(monkeypatch):
    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            _ = kwargs
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="```c\nint a=0;\n```"))]
            )

    class FakeClient:
        def __init__(self, api_key=None, base_url=None):
            self.api_key = api_key
            self.base_url = base_url
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setattr(llm_caller.openai, "OpenAI", FakeClient)

    caller = LLMCaller(model="demo-model")
    text = caller.generate_code("hi")
    assert "int a=0;" in text
