
import argparse
import yaml
import os
from dgf_header_parser.extractor import Extractor
from dgf_prompt_generator.generator import PromptGenerator
from dgf_feedback.feedback_controller import FeedbackController

def run_pipeline(config):
    extractor = Extractor(config['api_extraction']['header_dir'])
    extractor.extract_and_save(config['api_extraction']['extracted_api_json'])

    gen = PromptGenerator(api_json=config['api_extraction']['extracted_api_json'])
    gen.generate_samples(config['prompt_generation']['samples'], config['prompt_generation']['output_dir'])

    fc = FeedbackController(
        api_json=config['api_extraction']['extracted_api_json'],
        output_dir=config['feedback_iteration']['output_dir'],
        clang_path=config['validator']['clang_path'],
        include_dirs=config['validator']['include_dirs'],
        lib_dir=config['validator']['lib_dir'],
        libs=config['validator']['libs']
    )
    fc.run_iteration(num_samples=config['feedback_iteration']['samples_per_round'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    run_pipeline(config)
