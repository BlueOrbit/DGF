class SampleFilter:
    def __init__(self, coverage_threshold=10):
        self.threshold = coverage_threshold

    def filter_sample(self, coverage_value):
        return coverage_value >= self.threshold
