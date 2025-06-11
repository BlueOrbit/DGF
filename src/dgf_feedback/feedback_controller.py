import os
from prompt_template import PromptTemplate
from llm_caller import LLMCaller
from validator import Validator
from runner import Runner
from coverage_collector import CoverageCollector
from sample_filter import SampleFilter
from prompt_rewriter import PromptRewriter

class FeedbackController:
    def __init__(self, api_json, output_dir):
        self.prompt_template = PromptTemplate(api_json)
        self.llm = LLMCaller()
        self.validator = Validator(clang_path="clang-14")
        self.runner = Runner()
        self.cov_collector = CoverageCollector()
        self.sample_filter = SampleFilter()
        self.rewriter = PromptRewriter(self.prompt_template)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run_iteration(self, num_samples=5):
        successful_samples = []

        for i in range(num_samples):
            prompt = self.rewriter.rewrite_prompt(len(successful_samples))
            code = self.llm.generate_code(prompt)

            start = code.find("```c")
            end = code.find("```", start + 4)
            if start != -1 and end != -1:
                code = code[start + 4:end].strip()
            else:
                print(f"Warning: No valid code block found in generated code for sample {i}. Using full code.")
            code = code.strip()

            src_path = os.path.join(self.output_dir, f"fuzz_driver_{i}.c")
            with open(src_path, "w") as f:
                f.write(code)

            success, binary = self.validator.validate_source(src_path, include_dirs=["../../testdata/cJSON"])
            if not success:
                continue

            work_dir = os.path.dirname(binary)
            os.environ["LLVM_PROFILE_FILE"] = os.path.join(work_dir, "default.profraw")

            if not self.runner.run_binary(binary):
                continue

            cov_result = self.cov_collector.collect_and_analyze(binary, work_dir)
            print(f"Coverage result: {cov_result}")

            if self.sample_filter.filter_sample(cov_result):
                successful_samples.append(code)

        return successful_samples
