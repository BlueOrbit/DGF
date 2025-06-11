import argparse
from dgf_header_parser.extractor import Extractor
from dgf_prompt_generator.generator import PromptGenerator
from dgf_feedback.feedback_controller import FeedbackController

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_json', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--samples', type=int, default=10)
    args = parser.parse_args()

    # 直接调用
    fc = FeedbackController(api_json=args.api_json, output_dir=args.output_dir)
    fc.run_iteration(num_samples=args.samples)
