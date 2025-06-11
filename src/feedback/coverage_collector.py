import subprocess
import os
import json

class CoverageCollector:
    def __init__(self, profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_coverage(self, binary_path, work_dir):
        profraw = os.path.join(work_dir, "default.profraw")
        profdata_out = os.path.join(work_dir, "default.profdata")

        # Merge profraw
        subprocess.run([self.profdata, "merge", "-sparse", profraw, "-o", profdata_out], check=True)

        # Export coverage json
        coverage_json = os.path.join(work_dir, "coverage.json")
        subprocess.run(
            [self.cov, "export", binary_path, "--instr-profile", profdata_out, "--format=text"],
            stdout=open(coverage_json, "w"),
            check=True
        )
        return coverage_json

    def parse_coverage(self, coverage_json):
        with open(coverage_json, 'r') as f:
            text = f.read()
        total_lines = sum(1 for line in text.splitlines() if "Line" in line and "Region" in line)
        return total_lines
