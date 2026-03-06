import json

from dgf_prompt_generator.prompt_template import PromptTemplate


def test_prompt_template_filters_prefix_and_generates_signature(tmp_path):
    api_json = tmp_path / "api.json"
    api_json.write_text(
        json.dumps(
            [
                {
                    "file": "x.h",
                    "result": {
                        "functions": [
                            {
                                "name": "cJSON_AddObjectToObject",
                                "result_type": "void",
                                "parameters": [{"name": "obj", "type": "void*"}],
                            },
                            {
                                "name": "OtherFunc",
                                "result_type": "int",
                                "parameters": [],
                            },
                        ]
                    },
                }
            ]
        )
    )

    template = PromptTemplate(
        str(api_json),
        system_includes=["stdint.h", "cJSON.h"],
        api_prefixes=["cJSON"],
    )

    all_names = template.get_all_api_names()
    assert all_names == ["cJSON_AddObjectToObject"]

    prompt = template.generate_prompt_from_api_list(["cJSON_AddObjectToObject"])
    assert "#include <cJSON.h>" in prompt
    assert "cJSON_AddObjectToObject" in prompt


def test_prompt_template_generate_prompt_uses_int_signature_and_prefix_filter(tmp_path):
    api_json = tmp_path / "api.json"
    api_json.write_text(
        json.dumps(
            [
                {
                    "file": "x.h",
                    "result": {
                        "functions": [
                            {
                                "name": "cJSON_Parse",
                                "result_type": "int",
                                "parameters": [],
                            },
                            {
                                "name": "OtherFunc",
                                "result_type": "void",
                                "parameters": [],
                            },
                        ]
                    },
                }
            ]
        )
    )

    template = PromptTemplate(str(api_json), api_prefixes=["cJSON"])
    prompt = template.generate_prompt(num_funcs=5)
    assert "int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)" in prompt
    assert "return 0;" in prompt
    assert "cJSON_Parse" in prompt
    assert "OtherFunc" not in prompt


def test_prompt_template_allows_empty_system_includes_and_negative_num_funcs(tmp_path):
    api_json = tmp_path / "api.json"
    api_json.write_text(
        json.dumps(
            [
                {
                    "file": "x.h",
                    "result": {
                        "functions": [
                            {
                                "name": "OnlyFunc",
                                "result_type": "void",
                                "parameters": [],
                            }
                        ]
                    },
                }
            ]
        )
    )

    template = PromptTemplate(str(api_json), system_includes=[])
    prompt = template.generate_prompt(num_funcs=-5)
    assert "#include <stdint.h>" not in prompt
    assert template.get_api_signatures(num_funcs=-5) == []
