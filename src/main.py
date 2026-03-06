import argparse
import json
import logging
import os

import yaml

from dgf_common.code_utils import extract_c_code_block
from dgf_common.logging_utils import configure_logging
from dgf_feedback.feedback_controller import FeedbackController
from dgf_header_parser.extractor import extract_all_api
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_prompt_generator.prompt_template import PromptTemplate

LOGGER = logging.getLogger(__name__)

def extract_api(config):
    """
    模块 1 + 2：执行API抽取
    """
    header_dir = config['api_extraction']['header_dir']
    include_dirs = config['api_extraction'].get('include_dirs', [])

    LOGGER.info("开始抽取API信息: %s", header_dir)
    results = extract_all_api(header_dir, include_dirs)

    output_path = config['api_extraction']['extracted_api_json']
    output_parent = os.path.dirname(output_path) or "."
    os.makedirs(output_parent, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    LOGGER.info("API信息保存至 %s", output_path)

def generate_seed_prompt(config):
    """
    模块 3：初始种子Prompt生成
    """
    api_json = config['api_extraction']['extracted_api_json']
    output_dir = config['prompt_generation']['output_dir']
    samples = config['prompt_generation'].get('samples', 5)
    num_funcs = config['prompt_generation'].get('num_funcs', 5)
    system_includes = config['prompt_generation'].get('system_includes', [])
    api_prefixes = config['prompt_generation'].get('api_prefixes', [])

    os.makedirs(output_dir, exist_ok=True)

    prompt_template = PromptTemplate(
        api_json,
        system_includes=system_includes,
        api_prefixes=api_prefixes,
    )
    llm = LLMCaller()

    LOGGER.info("开始生成 %d 个种子 Prompt", samples)

    for i in range(samples):
        prompt = prompt_template.generate_prompt(num_funcs=num_funcs)
        code = llm.generate_code(prompt)
        code = extract_c_code_block(code)

        with open(os.path.join(output_dir, f"fuzz_driver_{i}.c"), "w") as f:
            f.write(code)

    LOGGER.info("种子 Prompt 生成完成")

def run_feedback_loop(config):
    """
    模块 4 + 5：Feedback Greybox 循环
    """
    api_json = config['api_extraction']['extracted_api_json']
    output_dir = config['feedback_iteration']['output_dir']
    samples_per_round = config['feedback_iteration']['samples_per_round']
    system_includes = config['prompt_generation'].get('system_includes', [])
    api_prefixes = config['prompt_generation'].get('api_prefixes', [])
    fuzz_timeout_sec = config['feedback_iteration'].get('fuzz_timeout_sec', 20)

    clang_path = config['validator']['clang_path']
    include_dirs = config['validator']['include_dirs']
    lib_dir = config['validator']['lib_dir']
    libs = config['validator']['libs']

    LOGGER.info("开始反馈循环，输出目录: %s", output_dir)

    fc = FeedbackController(
        api_json=api_json,
        output_dir=output_dir,
        clang_path=clang_path,
        include_dirs=include_dirs,
        lib_dir=lib_dir,
        libs=libs,
        system_includes=system_includes,
        api_prefixes=api_prefixes,
        fuzz_timeout_sec=fuzz_timeout_sec,
    )
    LOGGER.info("FeedbackController 初始化完成")
    fc.run_iteration(num_samples=samples_per_round)
    LOGGER.info("反馈循环完成")

def main():
    configure_logging()
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
