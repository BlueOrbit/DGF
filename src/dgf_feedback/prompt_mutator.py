# src/dgf_feedback/prompt_mutator.py

import random

class PromptMutator:
    def __init__(self, api_manager):
        self.api_manager = api_manager

    def insert(self, current_apis, num_insert=1):
        remaining = list(set(self.api_manager.api_list) - set(current_apis))
        if not remaining:
            return current_apis  # 没有可插入API了
        inserts = random.sample(remaining, min(num_insert, len(remaining)))
        return current_apis + inserts

    def replace(self, current_apis, num_replace=1):
        if not current_apis:
            return current_apis
        replace_num = min(num_replace, len(current_apis))
        indices = random.sample(range(len(current_apis)), replace_num)
        remaining = list(set(self.api_manager.api_list) - set(current_apis))
        for idx in indices:
            if remaining:
                new_api = random.choice(remaining)
                current_apis[idx] = new_api
                remaining.remove(new_api)
        return list(set(current_apis))

    def crossover(self, parent_apis1, parent_apis2):
        merged = list(set(parent_apis1) | set(parent_apis2))
        return merged

    def mutate(self, current_apis, parents=None):
        mode = random.choice(["insert", "replace", "crossover"])
        if mode == "insert":
            return self.insert(current_apis)
        elif mode == "replace":
            return self.replace(current_apis)
        elif mode == "crossover" and parents is not None:
            return self.crossover(current_apis, parents)
        else:
            return current_apis  # 保底返回
