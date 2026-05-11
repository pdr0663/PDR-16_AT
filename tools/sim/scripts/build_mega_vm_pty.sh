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
CC_BIN="${CC:-cc}"

mkdir -p "${OUT_DIR}"

SIMAVR_INCLUDE_DIR="$(simavr_find_header_dir || true)"
PARTS_INCLUDE_DIR="$(simavr_find_parts_header_dir || true)"
SIMAVR_LIB_DIR="$(simavr_find_lib_dir || true)"
PARTS_LIB_DIR="$(simavr_find_parts_lib_dir || true)"

missing=0
if [[ -z "${SIMAVR_INCLUDE_DIR}" || ! -f "${SIMAVR_INCLUDE_DIR}/sim_avr.h" ]]; then
  echo "Could not find simavr headers (sim_avr.h)." >&2
  missing=1
fi
if [[ -z "${PARTS_INCLUDE_DIR}" || ! -f "${PARTS_INCLUDE_DIR}/uart_pty.h" ]]; then
  echo "Could not find simavr parts headers (uart_pty.h)." >&2
  missing=1
fi
if [[ -z "${SIMAVR_LIB_DIR}" || ! -e "${SIMAVR_LIB_DIR}/libsimavr.so" && ! -e "${SIMAVR_LIB_DIR}/libsimavr.so.1" && ! -e "${SIMAVR_LIB_DIR}/libsimavr.a" ]]; then
  echo "Could not find libsimavr in a known library directory." >&2
  missing=1
fi
if [[ -z "${PARTS_LIB_DIR}" || ! -e "${PARTS_LIB_DIR}/libsimavrparts.so" && ! -e "${PARTS_LIB_DIR}/libsimavrparts.so.1" && ! -e "${PARTS_LIB_DIR}/libsimavrparts.a" ]]; then
  echo "Could not find libsimavrparts in a known library directory." >&2
  missing=1
fi

if [[ "${missing}" -ne 0 ]]; then
  cat >&2 <<EOF

Searched using SIMAVR_ROOT=${SIMAVR_ROOT}

Supported setup options:
  1. Repo-local source build:
       ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh
       ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh

     If Codex cannot reach GitHub but you can provide an archive:
       SIMAVR_ARCHIVE=/path/to/simavr.tar.gz ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh

  2. System packages, if available in your environment:
       apt-get update
       apt-get install -y simavr libsimavr-dev

  3. Explicit paths to prebuilt artifacts:
       SIMAVR_INCLUDE_DIR=/path/to/simavr/sim \\
       SIMAVR_PARTS_INCLUDE_DIR=/path/to/examples/parts \\
       SIMAVR_LIB_DIR=/path/to/simavr/obj-x86_64-linux-gnu \\
       SIMAVR_PARTS_LIB_DIR=/path/to/examples/parts/obj-x86_64-linux-gnu \\
       ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh

Run this diagnostic for details:
  ${REPO_ROOT}/tools/sim/scripts/doctor_simavr.sh
EOF
  exit 1
fi

cflags=("${SRC_PATH}" "-I${SIMAVR_INCLUDE_DIR}" "-I${PARTS_INCLUDE_DIR}")
ldflags=(
  "-L${SIMAVR_LIB_DIR}"
  "-L${PARTS_LIB_DIR}"
  "-Wl,-rpath,${SIMAVR_LIB_DIR}"
  "-Wl,-rpath,${PARTS_LIB_DIR}"
  -lsimavrparts -lsimavr -lelf -lpthread -lutil
)

if [[ -n "${SIMAVR_EXTRA_CFLAGS:-}" ]]; then
  # shellcheck disable=SC2206
  cflags+=( ${SIMAVR_EXTRA_CFLAGS} )
fi
if [[ -n "${SIMAVR_EXTRA_LDFLAGS:-}" ]]; then
  # shellcheck disable=SC2206
  ldflags+=( ${SIMAVR_EXTRA_LDFLAGS} )
fi

"${CC_BIN}" -o "${OUT_PATH}" "${cflags[@]}" "${ldflags[@]}"
chmod +x "${OUT_PATH}"

echo "Built ${OUT_PATH}"
echo "  simavr headers: ${SIMAVR_INCLUDE_DIR}"
echo "  parts headers:  ${PARTS_INCLUDE_DIR}"
echo "  simavr libs:    ${SIMAVR_LIB_DIR}"
echo "  parts libs:     ${PARTS_LIB_DIR}"
