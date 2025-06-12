import json
import random
from dgf_header_parser.constraint_inferencer import ConstraintInferencer

class PromptTemplate:
    def __init__(self, api_info_json):
        # 加载API信息
        self.api_data = json.load(open(api_info_json))
        self.system_includes = [
            "stdint.h", "stddef.h", "stdio.h",
            "stdlib.h", "string.h", "cJSON.h", "cJSON_Utils.h"
        ]

        # 约束推导初始化
        inferencer = ConstraintInferencer(self.api_data)
        self.constraints = inferencer.infer_constraints()

    def get_all_api_names(self):
        functions = []
        for file_entry in self.api_data:
            functions.extend([f["name"] for f in file_entry["result"]["functions"]])
        return functions

    def generate_prompt(self, num_funcs=5):
        selected_funcs = self.get_api_signatures(num_funcs)
        return self._generate_prompt_from_funcs(selected_funcs)

    def generate_prompt_from_api_list(self, api_names):
        all_funcs = []
        for file_entry in self.api_data:
            all_funcs.extend(file_entry["result"]["functions"])

        selected_funcs = [func for func in all_funcs if func["name"] in api_names]
        return self._generate_prompt_from_funcs(selected_funcs, api_names)

    def _generate_prompt_from_funcs(self, selected_funcs, api_names):
        includes = "\n".join([f"#include <{hdr}>" for hdr in self.system_includes])
        func_signatures = "\n".join(
            [self.format_func_signature(func) for func in selected_funcs]
        )

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

    def get_api_signatures(self, num_funcs=5):
        functions = []
        for file_entry in self.api_data:
            functions.extend(file_entry["result"]["functions"])
        selected_funcs = random.sample(functions, min(num_funcs, len(functions)))
        return selected_funcs

    def format_func_signature(self, func):
        params = []
        for param in func['parameters']:
            param_str = f"{param['type']} {param['name']}"
            param_constraints = self.get_param_constraints(func['name'], param['name'])
            if param_constraints:
                constraint_desc = " /* " + ", ".join(param_constraints) + " */"
                param_str += constraint_desc
            params.append(param_str)
        return f"{func['result_type']} {func['name']}({', '.join(params)});"

    def get_param_constraints(self, func_name, param_name):
        cons = self.constraints.get(func_name, [])
        res = []
        for c in cons:
            if c["param"] == param_name:
                desc = self.constraint_to_instruction(c["type"])
                if desc:
                    res.append(desc)
        return res

    def constraint_to_instruction(self, constraint_type):
        if constraint_type == "ArrayLength":
            return "use FuzzedDataProvider.ConsumeInt() for length"
        if constraint_type == "ArrayIndex":
            return "use FuzzedDataProvider.ConsumeInt() for index"
        if constraint_type == "AllocSize":
            return "use FuzzedDataProvider.ConsumeInt() for allocation size"
        if constraint_type == "FileName":
            return "use FuzzedDataProvider.ConsumeRandomLengthString() for filename"
        if constraint_type == "FormatString":
            return "use fixed valid format string"
        return None
