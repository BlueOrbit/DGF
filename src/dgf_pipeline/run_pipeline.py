import argparse

from dgf_common.logging_utils import configure_logging

# from dgf_header_parser.extractor import Extractor
# from dgf_prompt_generator.generator import PromptGenerator
from dgf_feedback.feedback_controller import FeedbackController

if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_json', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--samples', type=int, default=10)
    parser.add_argument("--clang_path", type=str, default="clang")
    parser.add_argument("--include_dirs", nargs="*", default=[])
    parser.add_argument("--lib_dir", type=str, default=None)
    parser.add_argument("--libs", nargs="*", default=[])
    parser.add_argument("--system_includes", nargs="*", default=None)
    parser.add_argument("--api_prefixes", nargs="*", default=None)
    parser.add_argument("--fuzz_timeout_sec", type=int, default=20)
    args = parser.parse_args()

    # 直接调用
    fc = FeedbackController(
        api_json=args.api_json,
        output_dir=args.output_dir,
        clang_path=args.clang_path,
        include_dirs=args.include_dirs,
        lib_dir=args.lib_dir,
        libs=args.libs,
        system_includes=args.system_includes,
        api_prefixes=args.api_prefixes,
        fuzz_timeout_sec=args.fuzz_timeout_sec,
    )
    fc.run_iteration(num_samples=args.samples)
