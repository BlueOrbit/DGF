from dgf_common.code_utils import extract_c_code_block


def test_extract_c_code_block_from_fenced_markdown():
    raw = "hello\n```c\nint x = 1;\n```\nbye"
    assert extract_c_code_block(raw) == "int x = 1;"


def test_extract_c_code_block_fallback_to_raw_text():
    raw = "int y = 2;"
    assert extract_c_code_block(raw) == "int y = 2;"


def test_extract_c_code_block_does_not_treat_python_fence_as_c():
    raw = "```python\nprint('x')\n```"
    assert extract_c_code_block(raw) == raw


def test_extract_c_code_block_supports_untagged_fence():
    raw = "prefix\n```\nint z = 3;\n```\nsuffix"
    assert extract_c_code_block(raw) == "int z = 3;"
