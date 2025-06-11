from validator import Validator
from runner import Runner

validator = Validator(clang_path="clang-14")
runner = Runner()

# 你的 fuzz driver 生成目录
for i in range(5):
    src_file = f"../fuzz_output/fuzz_driver_{i}.c"
    success, binary = validator.validate_source(src_file)
    if success:
        runner.run_binary(binary)
