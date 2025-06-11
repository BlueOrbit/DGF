import argparse
from prompt_template import PromptTemplate
from llm_caller import LLMCaller
from tqdm import tqdm
import os

def main(args):
    prompt_gen = PromptTemplate(args.api_json)
    llm = LLMCaller()

    os.makedirs(args.output_dir, exist_ok=True)

    for i in tqdm(range(args.samples)):
        prompt = prompt_gen.generate_prompt(num_funcs=args.num_funcs)
        code = llm.generate_code(prompt)

        output_path = f"{args.output_dir}/fuzz_driver_{i}.c"
        with open(output_path, "w") as f:
            f.write(code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_json", required=True, help="Extracted API JSON")
    parser.add_argument("--output_dir", required=True, help="Directory to save generated fuzz drivers")
    parser.add_argument("--samples", type=int, default=5, help="Number of fuzz drivers to generate")
    parser.add_argument("--num_funcs", type=int, default=5, help="Number of APIs to include per driver")

    args = parser.parse_args()
    main(args)
