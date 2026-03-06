# Code Review Report

日期：2026-03-06  
范围：`/workspace` 全仓（核心流程、测试、CI、文档一致性）

## 1. Findings（按严重级别）

### High

1. `llvm-cov` 分支覆盖 JSON 解析假设过强，可能运行时崩溃  
   - 文件：`src/dgf_feedback/branch_coverage_collector.py`  
   - 风险：`branches` 元素并非总是 dict，旧实现会触发异常。

2. 外部工具缺失时异常未兜底（clang / llvm-profdata / llvm-cov / fuzz binary）  
   - 文件：`src/dgf_validator/validator.py`, `src/dgf_validator/fuzzer_runner.py`, `src/dgf_feedback/branch_coverage_collector.py`  
   - 风险：环境差异直接导致 pipeline 硬失败。

3. API 抽取未按“目标头文件”过滤，可能混入系统或依赖头符号  
   - 文件：`src/dgf_header_parser/ast_parser.py`, `src/dgf_header_parser/extractor.py`  
   - 风险：Prompt API 污染，编译成功率下降。

### Medium

4. `api_prefixes` 在随机采样路径未生效  
   - 文件：`src/dgf_prompt_generator/prompt_template.py`  
   - 风险：配置与行为不一致。

5. Prompt 中 `LLVMFuzzerTestOneInput` 签名不符合常用约定  
   - 文件：`src/dgf_prompt_generator/prompt_template.py`  
   - 风险：生成代码兼容性风险。

6. API 级覆盖缺失时样本过滤过于严格，反馈学习可能停滞  
   - 文件：`src/dgf_feedback/sample_filter.py`, `src/dgf_feedback/feedback_controller.py`  
   - 风险：反馈迭代长期不更新。

7. standalone pipeline 参数能力低于主流程  
   - 文件：`src/dgf_pipeline/run_pipeline.py`  
   - 风险：复现实验与调参受限。

8. 提取器 CLI 未确保输出目录存在  
   - 文件：`src/dgf_header_parser/extractor.py`  
   - 风险：命令行独立运行易失败。

### Low

9. 代码块提取可能误拿非 C 代码块  
   - 文件：`src/dgf_common/code_utils.py`

10. CI 版本覆盖和依赖稳定性不足  
   - 文件：`.github/workflows/ci.yml`, `requirements*.txt`, `README.md`

## 2. 已实施修复

- 覆盖率解析增强：兼容 `dict` 与 `list/tuple` branch schema；支持 `data.files.functions` 与 `data.functions` 两种结构；异常降级为安全返回。  
- 外部命令健壮性增强：统一处理 `FileNotFoundError/OSError`；编译前检查 `clang` 可用性并输出明确错误。  
- AST 抽取过滤：仅保留来自当前目标 header 的声明节点。  
- Prompt 生成修复：`api_prefixes` 对随机采样生效；fuzzer 入口签名改为 `int ...` 且包含 `return 0;`。  
- 反馈过滤降级：当 API 级覆盖缺失时，支持按 overall coverage 判定。  
- pipeline 参数补齐：新增 `--system_includes --api_prefixes --fuzz_timeout_sec`。  
- extractor CLI 修复：输出路径父目录自动创建。  
- 代码块提取改进：优先匹配 C/C++ fenced block。  
- 工程化增强：CI 改为 Python 3.9/3.10/3.11 matrix，并加 import smoke。  
- 依赖稳定性增强：`requirements.txt` 和 `requirements-dev.txt` 固定版本。  
- 文档同步：README 补充 cJSON 构建步骤与更新后的 pipeline 参数示例。

## 3. 新增/增强测试

- `tests/test_branch_coverage_collector.py`：覆盖 mixed schema、invalid JSON、tool missing。  
- `tests/test_ast_parser.py`：覆盖 header 来源过滤逻辑。  
- `src/dgf_validator/test_validator.py`：新增缺少编译器、重试成功、重试失败分支测试。  
- `src/dgf_feedback/test_feedback.py`：补充过滤失败、overall fallback、随机稳定性。  
- `src/dgf_prompt_generator/test_prompt_gen.py`：补充 fuzzer 签名断言与 prefix 采样断言。  
- `tests/test_code_utils.py`：补充“优先提取 C fenced block”断言。

## 4. 验证结果

- `python3 -m ruff check src tests` ✅  
- `python3 -m mypy src` ✅  
- `python3 -m pytest` ✅（23 passed）

## 5. 残余风险

- 覆盖率函数名与 API 名映射仍基于名称匹配，复杂工程下可能需要更强映射策略（符号表或插桩映射）。
