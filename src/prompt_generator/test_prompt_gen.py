import os

# 你需要先导出你的 OPENAI API KEY
os.environ["OPENAI_API_KEY"] = "你的API KEY"

from prompt_template import PromptTemplate
from llm_caller import LLMCaller

prompt_gen = PromptTemplate("cjson_extracted.json")
llm = LLMCaller()

prompt = prompt_gen.generate_prompt(num_funcs=3)
print("======== Prompt ========")
print(prompt)

code = llm.generate_code(prompt)
print("======== Generated Code ========")
print(code)
