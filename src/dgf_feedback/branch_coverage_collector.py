# src/dgf_feedback/branch_coverage_collector.py

import json
import logging
import os
import subprocess

LOGGER = logging.getLogger(__name__)

class BranchCoverageCollector:
    def __init__(self, profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_branch_coverage(self, binary_path, work_dir):
        profraw = os.path.join(work_dir, "default.profraw")
        profdata_out = os.path.join(work_dir, "default.profdata")

        if not os.path.exists(profraw):
            LOGGER.warning("Coverage profile file not found at %s", profraw)
            return {}, 0.0

        try:
            subprocess.run(
                [self.profdata, "merge", "-sparse", profraw, "-o", profdata_out],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            LOGGER.warning("Failed to merge profile data: %s", exc.stderr)
            return {}, 0.0

        export_cmd = [
            self.cov, "export",
            "--instr-profile", profdata_out,
            binary_path,
            "--format=json"
        ]
        try:
            result = subprocess.run(
                export_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )
            output = json.loads(result.stdout)
        except subprocess.CalledProcessError as exc:
            LOGGER.warning("Failed to export coverage json: %s", exc.stderr)
            return {}, 0.0
        except json.JSONDecodeError:
            LOGGER.warning("Invalid coverage JSON output from llvm-cov")
            return {}, 0.0

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

        total_branches_all = 0
        covered_branches_all = 0

        for file_data in output.get("data", []):
            for func in file_data.get("functions", []):
                branches = func.get("branches", [])
                total_branches_all += len(branches)
                covered_branches_all += sum(1 for b in branches if b.get("count", 0) > 0)

        overall_coverage = covered_branches_all / total_branches_all if total_branches_all > 0 else 0.0

        # 可直接return两个指标
        return func_coverage, overall_coverage

