# src/dgf_validator/fuzzer_runner.py

import subprocess
import os

class FuzzerRunner:
    def __init__(self, timeout_sec=10, max_input_size=4096):
        self.timeout_sec = timeout_sec
        self.max_input_size = max_input_size

    def run_libfuzzer(self, binary_path, work_dir):
        os.makedirs(work_dir, exist_ok=True)

        cmd = [
            binary_path,
            "-max_len=" + str(self.max_input_size),
            "-runs=0",
            "-max_total_time=" + str(self.timeout_sec),
            "-print_final_stats=1",
            "-close_fd_mask=3"
        ]

        print("Launching libFuzzer run:", " ".join(cmd))

        try:
            subprocess.run(cmd, timeout=self.timeout_sec + 5, check=True)
            return True
        except subprocess.TimeoutExpired:
            print(f"Fuzzing timeout for {binary_path}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Fuzzing crash detected for {binary_path}")
            return False
