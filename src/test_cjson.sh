#!/bin/bash

set -e

# 激活 miniconda 环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dgf310

# 下载 cJSON 库作为测试目标
mkdir -p testdata
cd testdata

if [ ! -d "cJSON" ]; then
    git clone https://github.com/DaveGamble/cJSON.git
fi

cd ..

# 设置 LIBCLANG_PATH（注意按你机器实际路径填写）
export LIBCLANG_PATH="/usr/lib/llvm-14/lib/libclang.so.1"

# 执行 header_parser 模块
python3 header_parser/extractor.py \
    --header_dir testdata/cJSON \
    --include_dirs testdata/cJSON \
    --output data/cjson_extracted.json
