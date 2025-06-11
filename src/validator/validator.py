import subprocess
import os

class Validator:
    def __init__(self, clang_path="clang-14", work_dir="./validated"):
        self.clang = clang_path
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

        # 补充通用库依赖
        self.extra_link_flags = [
            "-lm", "-lpthread", "-ldl"
        ]

        self.extra_link_flags = [
            "-lm", "-lpthread", "-ldl",
            "-L../testdata/cJSON/build", "-lcjson"
        ]

        # 可选: future 可切换成 libFuzzer runtime支持
        self.fuzzer_flags = [
            "-fsanitize=fuzzer,address,undefined",
            "-fno-sanitize-recover=all",
            "-O0", "-g"
        ]

    def validate_source(self, src_file, include_dirs=[]):
        output_binary = os.path.join(self.work_dir, os.path.basename(src_file).replace(".c", ""))

        compile_cmd = [self.clang] + self.fuzzer_flags

        # 源文件
        compile_cmd.append(src_file)

        # 头文件目录
        for inc in include_dirs:
            compile_cmd.extend(["-I", inc])

        # 链接库
        compile_cmd.extend(self.extra_link_flags)

        # 输出文件
        compile_cmd.extend(["-o", output_binary])

        print("Compiling:", " ".join(compile_cmd))

        try:
            subprocess.run(compile_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True, output_binary
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed for {src_file}:\n{e.stderr.decode()}")
            return False, None
