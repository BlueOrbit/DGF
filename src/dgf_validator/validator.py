import subprocess
import os
import re

class Validator:
    def __init__(self, clang_path="clang-14", work_dir="./validated"):
        self.clang = clang_path
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

        self.extra_link_flags = [
            "-lm", "-lpthread", "-ldl",
            "-L/home/lanjiachen/DGF/testdata/cJSON/build",
            "-lcjson", "-lcjson_utils"
        ]

        self.fuzzer_flags = [
            "-fsanitize=fuzzer,address,undefined",
            "-fno-sanitize-recover=all",
            "-O0", "-g"
        ]

    def validate_source(self, src_file, include_dirs=[], max_retry=3):
        output_binary = os.path.join(self.work_dir, os.path.basename(src_file).replace(".c", ""))

        for attempt in range(max_retry):
            compile_cmd = [self.clang] + self.fuzzer_flags + [src_file]
            for inc in include_dirs:
                compile_cmd.extend(["-I", inc])
            compile_cmd.extend(self.extra_link_flags)
            compile_cmd.extend(["-o", output_binary])

            print(f"Compiling (attempt {attempt+1}):", " ".join(compile_cmd))

            try:
                subprocess.run(compile_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True, output_binary
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr.decode()
                print(f"Compilation failed (attempt {attempt+1}):\n{stderr_output}")

                # 检测 undefined reference to `__xxx`
                undefined_refs = re.findall(r"undefined reference to `(__[a-zA-Z0-9_]+)`", stderr_output)
                if undefined_refs and attempt + 1 < max_retry:
                    # 尝试自动修复，追加 -lm
                    print("Detected undefined internal reference(s):", undefined_refs)
                    self.extra_link_flags.append("-lm")
                    print("AutoFixer: Retrying compilation with additional -lm")
                    continue
                else:
                    return False, None

        return False, None
