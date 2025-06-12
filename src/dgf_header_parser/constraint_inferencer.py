# src/dgf_header_parser/constraint_inferencer.py

import re

class ConstraintInferencer:
    def __init__(self, extracted_api_json):
        self.api_data = extracted_api_json

    def infer_constraints(self):
        constraints = {}

        for file_entry in self.api_data:
            for func in file_entry["result"]["functions"]:
                func_name = func["name"]
                constraints[func_name] = []

                for param in func["parameters"]:
                    pname = param["name"].lower()
                    ptype = param["type"].lower()

                    # ArrayLength constraint
                    if "length" in pname or pname.endswith("_len") or pname.endswith("_size"):
                        constraints[func_name].append({
                            "param": param["name"],
                            "type": "ArrayLength"
                        })

                    # ArrayIndex constraint (simplified heuristic)
                    if "index" in pname or pname.endswith("_idx"):
                        constraints[func_name].append({
                            "param": param["name"],
                            "type": "ArrayIndex"
                        })

                    # FileName constraint
                    if "file" in pname or pname.endswith("_path") or ptype == "const char *":
                        constraints[func_name].append({
                            "param": param["name"],
                            "type": "FileName"
                        })

                    # AllocSize constraint
                    if ("malloc" in func_name or "alloc" in func_name) and ("size" in pname or pname.endswith("_size")):
                        constraints[func_name].append({
                            "param": param["name"],
                            "type": "AllocSize"
                        })

                    # FormatString constraint
                    if "format" in pname:
                        constraints[func_name].append({
                            "param": param["name"],
                            "type": "FormatString"
                        })

        return constraints
