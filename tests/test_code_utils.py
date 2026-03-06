from dgf_common.code_utils import extract_c_code_block


def test_extract_c_code_block_from_fenced_markdown():
    raw = "hello\n```c\nint x = 1;\n```\nbye"
    assert extract_c_code_block(raw) == "int x = 1;"


def test_extract_c_code_block_fallback_to_raw_text():
    raw = "int y = 2;"
    assert extract_c_code_block(raw) == "int y = 2;"


def test_extract_c_code_block_prefers_c_fence_over_other_fences():
    raw = "```text\nnot c\n```\n```c\nint z = 3;\n```"
    assert extract_c_code_block(raw) == "int z = 3;"
