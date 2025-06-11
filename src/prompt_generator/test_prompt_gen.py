import config
from prompt_template import PromptTemplate
from llm_caller import LLMCaller

prompt_gen = PromptTemplate("/home/lanjiachen/DGF/src/data/cjson_extracted.json")
llm = LLMCaller()

prompt = prompt_gen.generate_prompt(num_funcs=3)
print("======== Prompt ========")
print(prompt)

code = llm.generate_code(prompt)
print("======== Generated Code ========")
print(code)

# Save the generated prompt and code to files
with open("../data/generated_prompt.txt", "w") as f:
    f.write(prompt)
with open("../data/generated_code.c", "w") as f:
    f.write(code)
