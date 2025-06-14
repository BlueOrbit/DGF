# DGF: 基于Prompt的Fuzz Driver自生成系统

> 本项目是 PromptFuzz 论文《Prompt Fuzzing for Fuzz Driver Generation》 (CCS 2024) 的全面复现实现，并扩展了调用链分析技术，用于增强 LLM 生成合理 API 调用系列的能力。

---

## 一、项目概述

DGF 自动生成高质量的 fuzz driver，进行应用程序库的默黑模糊测试，根据覆盖率反馈和程序验证进行迭代优化，复现 PromptFuzz 论文中的核心技术思路。

---

## 二、系统模块构成

```
头文件 --> 头文解析 (Header Parser) --> API 签名
      |
      v
  调用链分析 (Call Chain Analysis)
      |
      v
Prompt 生成 (Prompt Generator) --> LLM 生成代码
      |
      v
程序验证 (Validator)
      |
      v
覆盖率收集 (Coverage Collector)
      |
      v
Prompt 变异 (Prompt Mutation) <--- 反馈控制 (Feedback Controller)
```

---

## 三、目录结构

```
DGF-main/
|
├— src/
|    ├— main.py               # 总控制入口
|    ├— config/               # 配置文件
|    ├— dgf_header_parser/   # 头文解析和API提取
|    ├— dgf_prompt_generator/ # Prompt生成和LLM调用
|    ├— dgf_validator/       # 程序验证模块
|    ├— dgf_feedback/        # 反馈控制与覆盖率收集
|    └— dgf_pipeline/        # 完整流水线执行控制
|
└— README.md
```

---

## 四、快速使用

### 1.环境供与

- Python 3.8+
- clang, llvm, lcov, cmake
- 支持libFuzzer的编译环境
- 安装Python依赖:

```bash
python -m venv venv
source venv/bin/activate
pip install -r src/dgf_prompt_generator/requirements.txt
pip install -r src/dgf_validator/requirements.txt
pip install -r src/dgf_feedback/requirements.txt
```

### 2.目标库准备

将测试库的源码和头文件放入指定路径，如:

```
testdata/cJSON/
```

### 3.运行全流程

```bash
cd src/
python main.py --config config/experiment.yaml
```

### 4.运行结果

- 生成种子seed程序
- 生成fuzz driver并执行libFuzzer测试
- 生成覆盖率和bug报告

---

## 五、配置文件

根本配置文件位于 `config/experiment.yaml`，具体包括:

- `library_path`：库源码路径
- `header_path`：头文件路径
- `clang_bin`：clang编译器路径
- `llm_provider`：设置LLM接口和API密钥
- `mutation_params`：Prompt变异策略参数

---

## 六、项目特性

- 完全复现 PromptFuzz 核心设计
- 基于覆盖率的 Prompt 变异和能量调度
- 多阶验证（编译+sanitizer+fuzzing）
- 集成 AFLFast 风格的 API energy scheduling
- 增强 **调用链分析** (扩展部分)
- 支持可复现性实验

---

## 七、参考文献

- PromptFuzz: Prompt Fuzzing for Fuzz Driver Generation
- CCS 2024, Yunlong Lyu et al.
- 本实现在此基础上扩展了静态程序分析分支，增强了生成合理性

---


