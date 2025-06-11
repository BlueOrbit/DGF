import random

class PromptRewriter:
    def __init__(self, base_prompt_template):
        self.base_template = base_prompt_template

    def rewrite_prompt(self, prev_success_samples):
        # 简化策略：增加少量 API 调用数量作为强化逻辑
        new_num_funcs = min(10, len(prev_success_samples) + 3)
        return self.base_template.generate_prompt(num_funcs=new_num_funcs)
