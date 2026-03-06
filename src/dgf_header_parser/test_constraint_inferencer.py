from dgf_header_parser.constraint_inferencer import ConstraintInferencer


def test_infer_constraints_keeps_entries_from_same_function_name():
    api_data = [
        {
            "file": "a.h",
            "result": {
                "functions": [
                    {
                        "name": "dup_func",
                        "result_type": "void",
                        "parameters": [{"name": "input_len", "type": "size_t"}],
                    }
                ]
            },
        },
        {
            "file": "b.h",
            "result": {
                "functions": [
                    {
                        "name": "dup_func",
                        "result_type": "void",
                        "parameters": [{"name": "file_path", "type": "const char *"}],
                    }
                ]
            },
        },
    ]

    constraints = ConstraintInferencer(api_data).infer_constraints()
    assert "dup_func" in constraints
    params = {item["param"] for item in constraints["dup_func"]}
    assert {"input_len", "file_path"}.issubset(params)
