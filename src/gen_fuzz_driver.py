import argparse
import yaml
import json
import os

from dgf_header_parser.extractor import extract_all_api
from dgf_prompt_generator.prompt_template import PromptTemplate
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_feedback.feedback_controller import FeedbackController

def generate_seed_prompt(config):
    """
    模块 3：初始种子Prompt生成
    """
    api_json = config['api_extraction']['extracted_api_json']
    output_dir = config['prompt_generation']['output_dir']
    samples = config['prompt_generation'].get('samples', 5)
    num_funcs = config['prompt_generation'].get('num_funcs', 5)

    output_dir = "/home/lanjiachen/DGF/src/data/fuzz_output"
    samples = config['prompt_generation'].get('samples', 5)


    os.makedirs(output_dir, exist_ok=True)

    prompt_template = PromptTemplate(api_json)
    llm = LLMCaller()

    print(f"[*] 开始生成 {samples} 个 fuzz driver种子")

    for i in range(samples):
        prompt = prompt_template.generate_prompt(num_funcs=num_funcs)
        code = llm.generate_code(prompt)

        start = code.find("```c")
        end = code.find("```", start + 4)
        if start != -1 and end != -1:
            code = code[start + 4:end].strip()
        else:
            code = code.strip()

        with open(os.path.join(output_dir, f"fuzz_driver_{i}.c"), "w") as f:
            f.write(code)

        print(f"[*] 生成fuzz driver: fuzz_driver_{i}.c")

    print("[*] fuzz driver生成完成")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)


    generate_seed_prompt(config)


if __name__ == "__main__":
    main()
