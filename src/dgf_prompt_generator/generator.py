import argparse
import logging
import os

from tqdm import tqdm

from dgf_common.code_utils import extract_c_code_block
from dgf_common.logging_utils import configure_logging
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_prompt_generator.prompt_template import PromptTemplate

LOGGER = logging.getLogger(__name__)

def main(args):
    prompt_gen = PromptTemplate(
        args.api_json,
        system_includes=args.system_includes,
        api_prefixes=args.api_prefixes,
    )
    llm = LLMCaller()

    os.makedirs(args.output_dir, exist_ok=True)

    for i in tqdm(range(args.samples)):
        prompt = prompt_gen.generate_prompt(num_funcs=args.num_funcs)
        code = llm.generate_code(prompt)
        code = extract_c_code_block(code)

        output_path = f"{args.output_dir}/fuzz_driver_{i}.c"
        with open(output_path, "w") as f:
            f.write(code)
        LOGGER.info("Generated %s", output_path)

if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_json", required=True, help="Extracted API JSON")
    parser.add_argument("--output_dir", required=True, help="Directory to save generated fuzz drivers")
    parser.add_argument("--samples", type=int, default=5, help="Number of fuzz drivers to generate")
    parser.add_argument("--num_funcs", type=int, default=5, help="Number of APIs to include per driver")
    parser.add_argument(
        "--system_includes",
        nargs="*",
        default=[],
        help="Header includes to place into prompt (e.g. cJSON.h)",
    )
    parser.add_argument(
        "--api_prefixes",
        nargs="*",
        default=[],
        help="Only keep APIs with selected prefixes",
    )

    args = parser.parse_args()
    main(args)
