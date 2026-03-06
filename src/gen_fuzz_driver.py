import argparse
import logging
import os

import yaml

from dgf_common.code_utils import extract_c_code_block
from dgf_common.logging_utils import configure_logging
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_prompt_generator.prompt_template import PromptTemplate

LOGGER = logging.getLogger(__name__)

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

    LOGGER.info("开始生成 %d 个 fuzz driver 种子", samples)

    for i in range(samples):
        prompt = prompt_template.generate_prompt(num_funcs=num_funcs)
        code = llm.generate_code(prompt)
        code = extract_c_code_block(code)

        with open(os.path.join(output_dir, f"fuzz_driver_{i}.c"), "w") as f:
            f.write(code)

        LOGGER.info("生成 fuzz driver: fuzz_driver_%d.c", i)

    LOGGER.info("fuzz driver 生成完成")

def main():
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)


    generate_seed_prompt(config)


if __name__ == "__main__":
    main()
