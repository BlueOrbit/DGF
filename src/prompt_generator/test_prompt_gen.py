import config
from prompt_template import PromptTemplate
from llm_caller import LLMCaller
import time

prompt_gen = PromptTemplate("/home/lanjiachen/DGF/src/data/cjson_extracted.json")
llm = LLMCaller()

prompt = prompt_gen.generate_prompt(num_funcs=3)
print("======== Prompt ========")
print(prompt)

code = llm.generate_code(prompt)
print("======== Generated Code ========")
print(code)

# Save the generated prompt and code to files
timestamp = time.strftime("%Y%m%d_%H%M%S")
prompt_filename = f"../data/generated_prompt_{timestamp}.txt"
code_filename = f"../data/generated_code_{timestamp}.c"

with open(prompt_filename, "w") as f:
    f.write(prompt)
with open(code_filename, "w") as f:
    f.write(code)
