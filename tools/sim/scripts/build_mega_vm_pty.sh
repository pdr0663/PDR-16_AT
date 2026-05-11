#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"
REPO_ROOT="$(simavr_repo_root)"
SIMAVR_ROOT="$(simavr_default_root)"
SRC_PATH="${REPO_ROOT}/tools/sim/src/mega_vm_pty.c"
OUT_DIR="${REPO_ROOT}/tools/sim/build"
OUT_PATH="${OUT_DIR}/mega_vm_pty"

mkdir -p "${OUT_DIR}"

SIMAVR_OBJ_DIR="$(simavr_find_obj_dir "${SIMAVR_ROOT}/simavr")"
PARTS_OBJ_DIR="$(simavr_find_obj_dir "${SIMAVR_ROOT}/examples/parts")"

if [[ -z "${SIMAVR_OBJ_DIR}" || -z "${PARTS_OBJ_DIR}" ]]; then
  cat >&2 <<EOF
Could not find built simavr object directories under: ${SIMAVR_ROOT}
Expected directories like:
  ${SIMAVR_ROOT}/simavr/obj-*
  ${SIMAVR_ROOT}/examples/parts/obj-*

Bootstrap/build a local copy with:
  ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh

Or set SIMAVR_ROOT to an existing simavr checkout before running this script.
EOF
  exit 1
fi

cc -o "${OUT_PATH}" \
  "${SRC_PATH}" \
  -I"${SIMAVR_ROOT}/simavr/sim" \
  -I"${SIMAVR_ROOT}/examples/parts" \
  -L"${SIMAVR_OBJ_DIR}" \
  -L"${PARTS_OBJ_DIR}" \
  -Wl,-rpath,"${SIMAVR_OBJ_DIR}" \
  -Wl,-rpath,"${PARTS_OBJ_DIR}" \
  -lsimavrparts -lsimavr -lelf -lpthread -lutil

echo "Built ${OUT_PATH}"
