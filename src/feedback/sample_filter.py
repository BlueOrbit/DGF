class SampleFilter:
    def __init__(self, min_lines=10, min_coverage=5.0):
        self.min_lines = min_lines
        self.min_coverage = min_coverage

    def filter_sample(self, cov_result):
        if cov_result['covered_lines'] < self.min_lines:
            return False
        if cov_result['coverage_percent'] < self.min_coverage:
            return False
        return True

