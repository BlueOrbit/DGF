import subprocess
import os

class CoverageEvaluator:
    def __init__(self, clang_path="clang", profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_coverage(self, binary_path, profraw_path="default.profraw", profdata_out="default.profdata"):
        # Merge profraw
        subprocess.run([self.profdata, "merge", "-sparse", profraw_path, "-o", profdata_out], check=True)

        # Export coverage summary
        result = subprocess.run([self.cov, "report", binary_path, "-p", ".", "--instr-profile", profdata_out],
                                 stdout=subprocess.PIPE, check=True)
        print(result.stdout.decode())
