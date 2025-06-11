import subprocess
import os

class CoverageCollector:
    def __init__(self, profdata_path="llvm-profdata", cov_path="llvm-cov"):
        self.profdata = profdata_path
        self.cov = cov_path

    def collect_and_analyze(self, binary_path, work_dir):
        profraw = os.path.join(work_dir, "default.profraw")
        profdata_out = os.path.join(work_dir, "default.profdata")

        subprocess.run([self.profdata, "merge", "-sparse", profraw, "-o", profdata_out], check=True)

        result = subprocess.run(
            [self.cov, "report", binary_path, "--instr-profile", profdata_out],
            stdout=subprocess.PIPE, check=True
        )

        total_lines = 0
        covered_lines = 0

        for line in result.stdout.decode().splitlines():
            if "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) < 2:
                continue
            try:
                covered, total = parts[1].split("/")
                covered_lines += int(covered.strip())
                total_lines += int(total.strip())
            except:
                continue

        coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0

        return {
            "covered_lines": covered_lines,
            "total_lines": total_lines,
            "coverage_percent": coverage_percent
        }
