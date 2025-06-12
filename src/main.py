import argparse
import yaml
import json
import os

from dgf_header_parser.extractor import extract_all_api
from dgf_prompt_generator.prompt_template import PromptTemplate
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_feedback.feedback_controller import FeedbackController

def extract_api(config):
    """
    模块 1 + 2：执行API抽取
    """
    header_dir = config['api_extraction']['header_dir']
    include_dirs = config['api_extraction'].get('include_dirs', [])

    print(f"[*] 开始抽取API信息 from {header_dir}")
    results = extract_all_api(header_dir, include_dirs)

    output_path = config['api_extraction']['extracted_api_json']
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[*] API信息保存至 {output_path}")

def generate_seed_prompt(config):
    """
    模块 3：初始种子Prompt生成
    """
    api_json = config['api_extraction']['extracted_api_json']
    output_dir = config['prompt_generation']['output_dir']
    samples = config['prompt_generation'].get('samples', 5)
    num_funcs = config['prompt_generation'].get('num_funcs', 5)

    os.makedirs(output_dir, exist_ok=True)

    prompt_template = PromptTemplate(api_json)
    llm = LLMCaller()

    print(f"[*] 开始生成 {samples} 个种子 Prompt")

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

    print("[*] 种子Prompt生成完成")

def run_feedback_loop(config):
    """
    模块 4 + 5：Feedback Greybox 循环
    """
    api_json = config['api_extraction']['extracted_api_json']
    output_dir = config['feedback_iteration']['output_dir']
    samples_per_round = config['feedback_iteration']['samples_per_round']

    clang_path = config['validator']['clang_path']
    include_dirs = config['validator']['include_dirs']
    lib_dir = config['validator']['lib_dir']
    libs = config['validator']['libs']

    print(f"[*] 开始反馈循环，输出目录: {output_dir}")

    fc = FeedbackController(
        api_json=api_json,
        output_dir=output_dir,
        clang_path=clang_path,
        include_dirs=include_dirs,
        lib_dir=lib_dir,
        libs=libs
    )
    print("[*] 初始化 FeedbackController 完成")
    fc.run_iteration(num_samples=samples_per_round)
    print("[*] 反馈循环完成")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    extract_api(config)
    generate_seed_prompt(config)
    run_feedback_loop(config)

if __name__ == "__main__":
    main()
