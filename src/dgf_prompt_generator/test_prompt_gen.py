# from dgf_prompt_generator import config
from dgf_prompt_generator.prompt_template import PromptTemplate
from dgf_prompt_generator.llm_caller import LLMCaller
import time
import os

prompt_gen = PromptTemplate("/home/lanjiachen/DGF/src/data/cjson_extracted.json")
llm = LLMCaller()
apiname= ["cJSON_AddObjectToObject"]
prompt = prompt_gen.generate_prompt_from_api_list(apiname)
print("======== Prompt ========")
print(prompt)

code = llm.generate_code(prompt)
print("======== Generated Code ========")
print(code)

# Save the generated prompt and code to files
timestamp = time.strftime("%Y%m%d_%H%M%S")
prompt_filename = f"./data/generated_prompt_{timestamp}.txt"
code_filename = f"./data/generated_code_{timestamp}.c"

with open(prompt_filename, "w") as f:
    f.write(prompt)
with open(code_filename, "w") as f:
    f.write(code)
