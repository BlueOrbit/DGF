import subprocess
import os
import json

class CoverageCollector:
    def __init__(self, profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_function_coverage(self, binary_path, work_dir):
        profraw = os.path.join(work_dir, "default.profraw")
        profdata_out = os.path.join(work_dir, "default.profdata")

        subprocess.run([self.profdata, "merge", "-sparse", profraw, "-o", profdata_out], check=True)

        export_cmd = [
            self.cov, "export",
            "--instr-profile", profdata_out,
            binary_path,
            "--format=text"
        ]
        result = subprocess.run(export_cmd, stdout=subprocess.PIPE, check=True)
        output = result.stdout.decode()

        func_coverage = {}
        for line in output.splitlines():
            if line.startswith("FN:"):  # 函数行标识
                parts = line.split(":")
                if len(parts) >= 3:
                    func_name = parts[1].strip()
                    coverage_str = parts[2].strip().rstrip("%")
                    coverage = float(coverage_str) / 100.0
                    func_coverage[func_name] = coverage
        return func_coverage
