#!/usr/bin/env bash
set -euo pipefail

path_export='export PATH="$HOME/.local/bin:$HOME/bin:$PATH"'

for profile in "${HOME}/.bashrc" "${HOME}/.profile"; do
  touch "${profile}"
  if ! grep -Fq "${path_export}" "${profile}"; then
    printf '\n%s\n' "${path_export}" >> "${profile}"
  fi
done

export PATH="${HOME}/.local/bin:${HOME}/bin:${PATH}"
