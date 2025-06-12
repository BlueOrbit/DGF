# src/dgf_feedback/sample_filter.py

class SampleFilter:
    def __init__(self, min_api_coverage=0.2, min_success_ratio=0.5):
        """
        min_api_coverage: 单API最低覆盖率 (0~1)
        min_success_ratio: 组合中有多少API达到有效覆盖
        """
        self.min_api_coverage = min_api_coverage
        self.min_success_ratio = min_success_ratio

    def filter_sample(self, mutated_apis, func_coverage_result):
        valid = 0
        total = len(mutated_apis)

        for api in mutated_apis:
            coverage = func_coverage_result.get(api, 0.0)
            if coverage >= self.min_api_coverage:
                valid += 1

        success_ratio = valid / total if total > 0 else 0

        if success_ratio >= self.min_success_ratio:
            return True
        else:
            return False
