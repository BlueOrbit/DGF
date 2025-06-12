# src/dgf_feedback/api_manager.py

import random
from collections import defaultdict

class APIManager:
    def __init__(self, api_list, exponent=1.0):
        self.api_list = api_list  # list of api function names
        self.exponent = exponent
        self.seed_count = defaultdict(int)
        self.prompt_count = defaultdict(int)
        self.coverage = defaultdict(float)  # coverage ratio for each API (0.0 ~ 1.0)

    def update_coverage(self, api_name, coverage_ratio):
        self.coverage[api_name] = coverage_ratio

    def update_seed(self, api_name):
        self.seed_count[api_name] += 1

    def update_prompt(self, api_name):
        self.prompt_count[api_name] += 1

    def get_energy(self, api_name):
        cov = self.coverage[api_name]
        seed = self.seed_count[api_name]
        prompt = self.prompt_count[api_name]
        E = self.exponent
        denominator = (1 + seed) ** E * (1 + prompt) ** E
        return (1 - cov) / denominator

    def sample_api_combination(self, num_funcs):
        energies = {api: self.get_energy(api) for api in self.api_list}
        total_energy = sum(energies.values())
        if total_energy == 0:
            return random.sample(self.api_list, min(num_funcs, len(self.api_list)))

        weighted_probs = [energies[api] / total_energy for api in self.api_list]
        selected = random.choices(self.api_list, weights=weighted_probs, k=num_funcs)
        return list(set(selected))  # 去重

    def print_state(self):
        for api in self.api_list:
            print(f"{api}: cov={self.coverage[api]:.2f}, seed={self.seed_count[api]}, prompt={self.prompt_count[api]}, energy={self.get_energy(api):.4f}")
