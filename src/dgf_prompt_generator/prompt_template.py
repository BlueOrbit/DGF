import json
import random
from class_chain import CallChainAnalyzer

class PromptTemplate:
    def __init__(self, api_info_json):
        self.api_data = json.load(open(api_info_json))
        self.system_includes = ["stdint.h","stddef.h","stdio.h", "stdlib.h", "string.h", "cJSON.h", "cJSON_Utils.h"]

    def get_api_signatures(self, num_funcs=5):
        functions = []
        for file_entry in self.api_data:
            if file_entry.get("file") == "testdata/cJSON/cJSON.h":
                functions.extend(file_entry["result"]["functions"])
        selected_funcs = random.sample(functions, min(num_funcs, len(functions)))
        return selected_funcs

    def generate_prompt(self, num_funcs=5):
        selected_funcs = self.get_api_signatures(num_funcs)

        includes = "\n".join([f"#include <{hdr}>" for hdr in self.system_includes])
        func_signatures = "\n".join(
            [self.format_func_signature(func) for func in selected_funcs]
        )
        prompt = f"""You are generating a fuzz driver using LLVMFuzzerTestOneInput function.

Always include:
{includes}

{func_signatures}

Please implement the LLVMFuzzerTestOneInput function that uses these APIs.

void LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {{
    // Your implementation here
}}"""

        return prompt

    def format_func_signature(self, func):
        params = ", ".join([f"{p['type']} {p['name']}" for p in func['parameters']])
        return f"{func['result_type']} {func['name']}({params});"


    def get_all_api_names(self):
        functions = []
        for file_entry in self.api_data:
            functions.extend([f["name"] for f in file_entry["result"]["functions"]])
        return functions

    def generate_prompt_from_api_list(self, api_names):
        # 重新找到完整函数信息
        all_funcs = []
        for file_entry in self.api_data:
            all_funcs.extend(file_entry["result"]["functions"])

        selected_funcs = [func for func in all_funcs if func["name"] in api_names]
        includes = "\n".join([f"#include <{hdr}>" for hdr in self.system_includes])
        func_signatures = "\n".join([self.format_func_signature(func) for func in selected_funcs])

        analyzer = CallChainAnalyzer()
        chain_texts = []
        for name in api_names:
            chain_text = analyzer.get_call_chains_for_function(name)
            chain_texts.append(f"/* Reverse call chains for {name}:\n{chain_text}\n*/")
        
        prompt = f"""You are generating a fuzz driver using LLVMFuzzerTestOneInput function.

Always include:
{includes}

{func_signatures}

These are *reverse call chains*, showing which functions call the target API. 
This information may help you synthesize realistic usage patterns in your fuzz driver.
{callchain_section}

Please implement the LLVMFuzzerTestOneInput function that uses these APIs.

void LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {{
    // Your implementation here
}}"""
        return prompt

