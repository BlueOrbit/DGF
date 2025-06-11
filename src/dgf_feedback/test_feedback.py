import sys
import os
sys.path.append(os.path.abspath("../prompt_generator"))
sys.path.append(os.path.abspath("../validator"))

from feedback_controller import FeedbackController

fc = FeedbackController(api_json="../data/cjson_extracted.json", output_dir="../data/fuzz_output_round1")
successful = fc.run_iteration(num_samples=10)
print(f"Successful samples: {len(successful)}")
