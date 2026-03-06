#!/usr/bin/env bash
set -euo pipefail

# Install Python dev dependencies into user site-packages.
python3 -m pip install --user -r requirements-dev.txt

# Expose user-installed tool entrypoints from a stable HOME/bin directory.
mkdir -p "${HOME}/bin"
for tool in pytest ruff mypy; do
  if [ -x "${HOME}/.local/bin/${tool}" ]; then
    ln -sf "${HOME}/.local/bin/${tool}" "${HOME}/bin/${tool}"
  fi
done
