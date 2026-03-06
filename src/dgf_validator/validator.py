import logging
import os
import re
import subprocess

LOGGER = logging.getLogger(__name__)

class Validator:
    def __init__(
        self,
        clang_path="clang",
        work_dir="./validated",
        lib_dir=None,
        libs=None,
        extra_link_flags=None,
    ):
        self.clang = clang_path
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

        libs = libs or []
        self.extra_link_flags = ["-lm", "-lpthread", "-ldl"]
        if lib_dir:
            self.extra_link_flags.extend([f"-L{lib_dir}", f"-Wl,-rpath,{lib_dir}"])
        self.extra_link_flags.extend(_normalize_lib_flags(libs))
        if extra_link_flags:
            self.extra_link_flags.extend(extra_link_flags)

        self.fuzzer_flags = [
            "-fsanitize=fuzzer,address,undefined",
            "-fno-sanitize-recover=all",
            "-O0", "-g"
        ]

    def validate_source(self, src_file, include_dirs=None, max_retry=3):
        include_dirs = include_dirs or []
        output_binary = os.path.join(self.work_dir, os.path.basename(src_file).replace(".c", ""))

        for attempt in range(max_retry):
            compile_cmd = [self.clang] + self.fuzzer_flags + [src_file]
            for inc in include_dirs:
                compile_cmd.extend(["-I", inc])
            compile_cmd.extend(self.extra_link_flags)
            compile_cmd.extend(["-o", output_binary])

            LOGGER.info("Compiling (attempt %d): %s", attempt + 1, " ".join(compile_cmd))

            try:
                subprocess.run(
                    compile_cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                return True, output_binary
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr
                LOGGER.warning("Compilation failed (attempt %d):\n%s", attempt + 1, stderr_output)

                # 检测 undefined reference to `__xxx`
                undefined_refs = re.findall(r"undefined reference to `(__[a-zA-Z0-9_]+)`", stderr_output)
                if undefined_refs and attempt + 1 < max_retry:
                    # 尝试自动修复，追加 -lm
                    LOGGER.info("Detected undefined internal reference(s): %s", undefined_refs)
                    if "-lm" not in self.extra_link_flags:
                        self.extra_link_flags.append("-lm")
                    LOGGER.info("AutoFixer: retrying compilation with additional -lm")
                    continue
                else:
                    return False, None

        return False, None


def _normalize_lib_flags(libs):
    normalized = []
    for lib in libs:
        if lib.startswith("-l"):
            normalized.append(lib)
        else:
            normalized.append(f"-l{lib}")
    return normalized
