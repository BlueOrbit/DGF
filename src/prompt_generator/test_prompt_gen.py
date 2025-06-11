import config
from prompt_template import PromptTemplate
from llm_caller import LLMCaller

prompt_gen = PromptTemplate("/home/lanjiachen/DGF/src/cjson_extracted.json")
llm = LLMCaller()

prompt = prompt_gen.generate_prompt(num_funcs=3)
print("======== Prompt ========")
print(prompt)

code = llm.generate_code(prompt)
print("======== Generated Code ========")
print(code)
