import os
from dgf_prompt_generator.prompt_template import PromptTemplate
from dgf_prompt_generator.llm_caller import LLMCaller
from dgf_validator.validator import Validator
from dgf_validator.fuzzer_runner import FuzzerRunner
from dgf_feedback.coverage_collector import CoverageCollector
from dgf_feedback.sample_filter import SampleFilter

from dgf_feedback.api_manager import APIManager
from dgf_feedback.prompt_mutator import PromptMutator

import random

class FeedbackController:
    def __init__(self, api_json, output_dir):
        self.prompt_template = PromptTemplate(api_json)
        self.llm = LLMCaller()
        self.validator = Validator(clang_path="clang-14")
        self.fuzzer = FuzzerRunner(timeout_sec=20)
        self.cov_collector = CoverageCollector()
        self.sample_filter = SampleFilter()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 初始化 APIManager
        all_api_list = self.prompt_template.get_all_api_names()
        self.api_manager = APIManager(all_api_list)
        self.mutator = PromptMutator(self.api_manager)

    def run_iteration(self, num_samples=5, base_num_funcs=5):
        successful_samples = []
        history_api_combos = []

        for i in range(num_samples):
            # === 动态选取 APIs ===
            candidate_apis = self.api_manager.sample_api_combination(base_num_funcs)
            mutated_apis = self.mutator.mutate(candidate_apis)
            history_api_combos.append(mutated_apis)

            # 记录 prompt 使用次数
            for api in mutated_apis:
                self.api_manager.update_prompt(api)

            prompt = self.prompt_template.generate_prompt_from_api_list(mutated_apis)
            code = self.llm.generate_code(prompt)

            # 提取代码块
            start = code.find("```c")
            end = code.find("```", start + 4)
            if start != -1 and end != -1:
                code = code[start + 4:end].strip()
            else:
                code = code.strip()

            src_path = os.path.join(self.output_dir, f"fuzz_driver_{i}.c")
            with open(src_path, "w") as f:
                f.write(code)

            # 验证编译
            success, binary = self.validator.validate_source(src_path, include_dirs=["../testdata/cJSON"])
            if not success:
                continue

            work_dir = os.path.dirname(binary)
            os.environ["LLVM_PROFILE_FILE"] = os.path.join(work_dir, "default.profraw")

            if not self.fuzzer.run_libfuzzer(binary, work_dir):
                continue

            cov_result = self.cov_collector.collect_and_analyze(binary, work_dir)
            print(f"Coverage result: {cov_result}")

            # 覆盖率反馈更新
            func_cov_result = self.cov_collector.collect_function_coverage(binary, work_dir)
            for api in mutated_apis:
                if api in func_cov_result:
                    self.api_manager.update_coverage(api, func_cov_result[api])

            if not self.sample_filter.filter_sample(mutated_apis, func_cov_result):
                continue

        self.api_manager.print_state()
        return successful_samples, history_api_combos
