# src/dgf_feedback/branch_coverage_collector.py

import subprocess
import os
import json

class BranchCoverageCollector:
    def __init__(self, profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_branch_coverage(self, binary_path, work_dir):
        profraw = os.path.join(work_dir, "default.profraw")
        profdata_out = os.path.join(work_dir, "default.profdata")

        subprocess.run([self.profdata, "merge", "-sparse", profraw, "-o", profdata_out], check=True)

        export_cmd = [
            self.cov, "export",
            "--instr-profile", profdata_out,
            binary_path,
            "--format=json"
        ]
        result = subprocess.run(export_cmd, stdout=subprocess.PIPE, check=True)
        output = json.loads(result.stdout.decode())

        func_coverage = {}

        for file_data in output.get("data", []):
            for func in file_data.get("functions", []):
                name = func.get("name")
                regions = func.get("branches", [])
                if not regions:
                    continue
                total_branches = len(regions)
                covered_branches = sum(1 for b in regions if b.get("count", 0) > 0)
                cov_ratio = covered_branches / total_branches if total_branches > 0 else 0.0
                func_coverage[name] = cov_ratio

        return func_coverage
