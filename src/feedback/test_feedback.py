from feedback_controller import FeedbackController

fc = FeedbackController(api_json="../cjson_extracted.json", output_dir="../fuzz_output_round1")
successful = fc.run_iteration(num_samples=5)
print(f"Successful samples: {len(successful)}")
