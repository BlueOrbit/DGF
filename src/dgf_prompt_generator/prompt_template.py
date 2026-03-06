import json
import random

from dgf_header_parser.constraint_inferencer import ConstraintInferencer


class PromptTemplate:
    def __init__(self, api_info_json, system_includes=None, api_prefixes=None):
        with open(api_info_json, "r") as f:
            self.api_data = json.load(f)

        if system_includes is None:
            self.system_includes = [
                "stdint.h",
                "stddef.h",
                "stdio.h",
                "stdlib.h",
                "string.h",
            ]
        else:
            self.system_includes = system_includes
        self.api_prefixes = api_prefixes or []

        # 约束推导初始化
        inferencer = ConstraintInferencer(self.api_data)
        self.constraints = inferencer.infer_constraints()

    def get_all_api_names(self):
        functions = []
        for file_entry in self.api_data:
            for func in file_entry["result"]["functions"]:
                name = func["name"]
                if not self.api_prefixes or any(name.startswith(prefix) for prefix in self.api_prefixes):
                    functions.append(name)
        return sorted(set(functions))


    def generate_prompt(self, num_funcs=5):
        selected_funcs = self.get_api_signatures(num_funcs)
        return self._generate_prompt_from_funcs(selected_funcs)

    def generate_prompt_from_api_list(self, api_names):
        all_funcs = []
        for file_entry in self.api_data:
            all_funcs.extend(file_entry["result"]["functions"])

        selected_funcs = [func for func in all_funcs if func["name"] in api_names]
        return self._generate_prompt_from_funcs(selected_funcs)

    def _generate_prompt_from_funcs(self, selected_funcs):
        includes = "\n".join([f"#include <{hdr}>" for hdr in self.system_includes])
        func_signatures = "\n".join(
            [self.format_func_signature(func) for func in selected_funcs]
        )

        prompt = f"""You are generating a fuzz driver using LLVMFuzzerTestOneInput function.

Always include:
{includes}

{func_signatures}

Please implement the LLVMFuzzerTestOneInput function that uses these APIs.

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {{
    // Your implementation here
    return 0;
}}"""
        return prompt

    def get_api_signatures(self, num_funcs=5):
        functions = []
        for file_entry in self.api_data:
            for func in file_entry["result"]["functions"]:
                name = func["name"]
                if not self.api_prefixes or any(name.startswith(prefix) for prefix in self.api_prefixes):
                    functions.append(func)
        if not functions:
            return []
        try:
            safe_num_funcs = int(num_funcs)
        except (TypeError, ValueError):
            safe_num_funcs = 0
        safe_num_funcs = max(0, safe_num_funcs)
        selected_funcs = random.sample(functions, min(safe_num_funcs, len(functions)))
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
