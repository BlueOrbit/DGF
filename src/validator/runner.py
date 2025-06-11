import subprocess

class Runner:
    def __init__(self):
        pass

    def run_binary(self, binary_path, timeout_sec=5):
        try:
            subprocess.run([binary_path], timeout=timeout_sec, check=True)
            return True
        except subprocess.TimeoutExpired:
            print(f"Timeout running {binary_path}")
            return False
        except subprocess.CalledProcessError:
            print(f"Crash detected in {binary_path}")
            return False
