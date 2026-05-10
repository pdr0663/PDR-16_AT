#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SIMAVR_ROOT="${SIMAVR_ROOT:-/mnt/c/Users/Paul/simavr}"
SRC_PATH="${REPO_ROOT}/tools/sim/src/mega_vm_pty.c"
OUT_DIR="${REPO_ROOT}/tools/sim/build"
OUT_PATH="${OUT_DIR}/mega_vm_pty"

mkdir -p "${OUT_DIR}"

cc -o "${OUT_PATH}" \
  "${SRC_PATH}" \
  -I"${SIMAVR_ROOT}/simavr/sim" \
  -I"${SIMAVR_ROOT}/examples/parts" \
  -L"${SIMAVR_ROOT}/simavr/obj-x86_64-linux-gnu" \
  -L"${SIMAVR_ROOT}/examples/parts/obj-x86_64-linux-gnu" \
  -Wl,-rpath,"${SIMAVR_ROOT}/simavr/obj-x86_64-linux-gnu" \
  -Wl,-rpath,"${SIMAVR_ROOT}/examples/parts/obj-x86_64-linux-gnu" \
  -lsimavrparts -lsimavr -lelf -lpthread -lutil

echo "Built ${OUT_PATH}"
