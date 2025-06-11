import json
import random

class PromptTemplate:
    def __init__(self, api_info_json):
        self.api_data = json.load(open(api_info_json))
        self.system_includes = ["stdio.h", "stdlib.h", "string.h", "cJSON.h", "cJSON_Utils.h"]

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
