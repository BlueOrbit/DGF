import os
from validator import Validator
from runner import Runner

# 初始化模块
validator = Validator(clang_path="clang-14")
runner = Runner()

# LLM 生成输出目录
fuzz_output_dir = "../data/fuzz_output_test"
include_dirs = ["../testdata/cJSON", "/usr/include", "/usr/local/include"]

for filename in os.listdir(fuzz_output_dir):
    if filename.endswith(".c"):
        src_file = os.path.join(fuzz_output_dir, filename)
        success, binary = validator.validate_source(src_file, include_dirs=include_dirs)
        if success:
            runner.run_binary(binary)
