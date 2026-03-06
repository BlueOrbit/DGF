import re

_FENCED_C_CPP_PATTERN = re.compile(r"```(?:c|C|cpp|c\+\+)\s*(.*?)```", re.DOTALL)
_FENCED_UNTAGGED_PATTERN = re.compile(r"```[ \t]*\n(.*?)```", re.DOTALL)


def extract_c_code_block(raw_text):
    """
    Extract C/C++ code from markdown fenced block.
    If no fenced block is present, return stripped raw text.
    """
    if raw_text is None:
        return ""

    match = _FENCED_C_CPP_PATTERN.search(raw_text)
    if match:
        return match.group(1).strip()

    # Backward-compatible fallback for unlabeled fenced blocks.
    match = _FENCED_UNTAGGED_PATTERN.search(raw_text)
    if match:
        return match.group(1).strip()
    return raw_text.strip()
