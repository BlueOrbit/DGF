# src/dgf_validator/fuzzer_runner.py

import logging
import os
import subprocess

LOGGER = logging.getLogger(__name__)

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

        LOGGER.info("Launching libFuzzer run: %s", " ".join(cmd))
        env = os.environ.copy()
        try:
            subprocess.run(cmd, timeout=self.timeout_sec + 5, check=True, env=env)
            return True
        except subprocess.TimeoutExpired:
            LOGGER.warning("Fuzzing timeout for %s", binary_path)
            return False
        except subprocess.CalledProcessError:
            LOGGER.warning("Fuzzing crash detected for %s", binary_path)
            return False
        except OSError as exc:
            LOGGER.warning("Failed to execute fuzzer binary %s: %s", binary_path, exc)
            return False
