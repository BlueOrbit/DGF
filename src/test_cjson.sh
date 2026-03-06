#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

# 下载 cJSON 库作为测试目标
mkdir -p testdata
cd testdata

if [ ! -d "cJSON" ]; then
    git clone https://github.com/DaveGamble/cJSON.git
fi

cd ..

# 可选设置 LIBCLANG_PATH（按环境覆盖）
export LIBCLANG_PATH="${LIBCLANG_PATH:-/usr/lib/llvm-14/lib/libclang.so.1}"

# 执行 header_parser 模块
python3 src/dgf_header_parser/extractor.py \
    --header_dir testdata/cJSON \
    --include_dirs testdata/cJSON \
    --output data/cjson_extracted.json
