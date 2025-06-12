import re

class CallChainAnalyzer:
    def __init__(self):
        self.input_file = '/home/lanjiachen/DGF/src/data/reverse_callgraph.txt'
        self.lines = self._read_and_clean_lines()

    def _read_and_clean_lines(self):
        lines = []
        with open(self.input_file, 'r') as f:
            for line in f:
                i = 0
                while i < len(line) and (line[i].isspace() or line[i].isdigit()):
                    if line[i].isspace() and i > 0 and line[i - 1].isdigit():
                        i += 1
                        break
                    i += 1
                cleaned_line = line[i:].rstrip('\n')
                lines.append(cleaned_line)
        return lines

    def get_call_chains_for_function(self, target_func, max_shortest=10):
        # 找到目标函数的行索引
        target_indices = [
            i for i, line in enumerate(self.lines)
            if re.search(r'\b' + re.escape(target_func) + r'\s*\(', line)
        ]

        if not target_indices:
            return f"未找到函数 {target_func} 的调用"

        all_chains = []

        for target_index in target_indices:
            # 向上追踪
            call_chain_indices = [target_index]
            current_indent = len(self.lines[target_index]) - len(self.lines[target_index].lstrip())
            for j in range(target_index - 1, -1, -1):
                indent = len(self.lines[j]) - len(self.lines[j].lstrip())
                if indent < current_indent:
                    call_chain_indices.append(j)
                    current_indent = indent

            # 向下收集子调用
            down_indices = []
            base_indent = len(self.lines[target_index]) - len(self.lines[target_index].lstrip())
            for k in range(target_index + 1, len(self.lines)):
                indent = len(self.lines[k]) - len(self.lines[k].lstrip())
                if indent > base_indent:
                    down_indices.append(k)
                else:
                    break

            # 构造完整调用链
            full_chain = [self.lines[idx] for idx in reversed(call_chain_indices)]
            full_chain += [self.lines[idx] for idx in down_indices]
            all_chains.append(full_chain)

        # 选择最短的N个调用链
        shortest_chains = sorted(all_chains, key=lambda c: len(c))[:max_shortest]

        # 构造文本输出
        result = []
        for i, chain in enumerate(shortest_chains, 1):
            result.append(f"Call Chain {i} (Length: {len(chain)}):")
            # result.extend(chain)
            cleaned_chain = [re.sub(r'\s*<.*?>', '', line) for line in chain]
            result.extend(cleaned_chain)
            result.append("")  # 空行分隔

        return "\n".join(result)


analyzer = CallChainAnalyzer()
prompt_text = analyzer.get_call_chains_for_function("malloc")
print(prompt_text)
