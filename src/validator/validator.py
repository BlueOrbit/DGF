import subprocess
import os

class Validator:
    def __init__(self, clang_path="clang", work_dir="./validated"):
        self.clang = clang_path
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

    def validate_source(self, src_file):
        output_binary = os.path.join(self.work_dir, os.path.basename(src_file).replace(".c", ""))
        compile_cmd = [
            self.clang,
            "-fsanitize=address,undefined",
            "-g",
            "-O0",
            src_file,
            "-o",
            output_binary
        ]
        try:
            subprocess.run(compile_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True, output_binary
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed for {src_file}:\n{e.stderr.decode()}")
            return False, None
