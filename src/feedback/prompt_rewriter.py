class PromptRewriter:
    def __init__(self, base_prompt_template):
        self.base_template = base_prompt_template

    def rewrite_prompt(self, prev_success_count):
        num_funcs = 5 + min(prev_success_count, 5)  # 每轮逐渐增加API组合数量
        return self.base_template.generate_prompt(num_funcs=num_funcs)

