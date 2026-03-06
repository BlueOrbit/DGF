# DGF: 基于 Prompt 的 Fuzz Driver 自动生成系统

本项目实现了从头文件 API 抽取、Prompt 构造、LLM 代码生成、编译验证、fuzz 执行到覆盖率反馈迭代的完整流程。

## 1. 模块流程

```text
Header Parser -> Prompt Generator -> LLM Code -> Validator -> Fuzzer -> Coverage -> Feedback
```

核心入口：`src/main.py`

## 2. 目录结构

```text
.
├── src/
│   ├── main.py
│   ├── config/experiment.yaml
│   ├── dgf_header_parser/
│   ├── dgf_prompt_generator/
│   ├── dgf_validator/
│   ├── dgf_feedback/
│   ├── dgf_pipeline/
│   └── dgf_common/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## 3. 环境要求

- Python 3.9+
- clang/llvm（建议 14+）
- 支持 libFuzzer 的编译环境

可选环境变量：

- `OPENAI_API_KEY`（必需，除非使用本地 `src/dgf_prompt_generator/config.py`）
- `OPENAI_BASE_URL`（可选）
- `OPENAI_MODEL`（默认 `gpt-4.1-mini`）
- `OPENAI_TEMPERATURE`（默认 `0.2`）
- `LIBCLANG_PATH`（可选，如 `/usr/lib/llvm-14/lib/libclang.so.1`）

## 4. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 5. 目标库准备（以 cJSON 为例）

将目标库放到：

```text
testdata/cJSON
```

并确保其可被 clang include/link（`src/config/experiment.yaml` 已给出默认路径模板）。

示例构建步骤：

```bash
cd testdata/cJSON
cmake -S . -B build
cmake --build build -j
cd ../..
```

建议先确认目标库产物存在，再运行主流程：

```bash
ls testdata/cJSON/build | head
```

## 6. 运行方式

### 6.1 运行完整流程

```bash
PYTHONPATH=src python src/main.py --config src/config/experiment.yaml
```

### 6.2 单独运行 feedback pipeline

```bash
PYTHONPATH=src python src/dgf_pipeline/run_pipeline.py \
  --api_json data/extracted_api.json \
  --output_dir data/feedback_results \
  --samples 5 \
  --clang_path clang \
  --include_dirs testdata/cJSON \
  --lib_dir testdata/cJSON/build \
  --libs cjson cjson_utils \
  --system_includes stdint.h stddef.h stdio.h stdlib.h string.h cJSON.h cJSON_Utils.h \
  --api_prefixes cJSON \
  --fuzz_timeout_sec 20
```

## 7. 配置说明

主配置：`src/config/experiment.yaml`

- `api_extraction`：头文件扫描路径、include 路径、抽取 JSON 输出位置
- `prompt_generation`：seed driver 数量、每个 driver 的 API 数、include 模板、API 前缀过滤
- `feedback_iteration`：每轮样本数与 fuzz 超时
- `validator`：clang 路径、include 路径、库目录与库名

## 8. 开发与质量检查

```bash
ruff check src
mypy src
pytest
```

仓库已包含 GitHub Actions 工作流（`.github/workflows/ci.yml`）用于自动执行上述检查。

## 9. 本地 LLM 配置（可选）

如不想依赖环境变量，可复制：

```text
src/dgf_prompt_generator/config.example.py -> src/dgf_prompt_generator/config.py
```

并填写 API 配置。`config.py` 默认不提交到仓库。
