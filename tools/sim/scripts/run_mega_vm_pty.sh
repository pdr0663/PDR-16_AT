#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"
REPO_ROOT="$(simavr_repo_root)"
BIN_PATH="${BIN_PATH:-${REPO_ROOT}/tools/sim/build/mega_vm_pty}"
FIRMWARE_PATH="${FIRMWARE_PATH:-${REPO_ROOT}/firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex}"
MCU="${MCU:-atmega2560}"
F_CPU="${F_CPU:-16000000}"

if [[ ! -x "${BIN_PATH}" ]]; then
  echo "PTY harness not found: ${BIN_PATH}" >&2
  echo "Build it first with ${SCRIPT_DIR}/build_mega_vm_pty.sh" >&2
  exit 1
fi

if [[ ! -f "${FIRMWARE_PATH}" ]]; then
  echo "Firmware not found: ${FIRMWARE_PATH}" >&2
  exit 1
fi

SIMAVR_LD_LIBRARY_PATH="$(simavr_library_path || true)"
if [[ -n "${SIMAVR_LD_LIBRARY_PATH}" ]]; then
  if [[ -n "${LD_LIBRARY_PATH:-}" ]]; then
    export LD_LIBRARY_PATH="${SIMAVR_LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}"
  else
    export LD_LIBRARY_PATH="${SIMAVR_LD_LIBRARY_PATH}"
  fi
fi

exec "${BIN_PATH}" --firmware "${FIRMWARE_PATH}" --mcu "${MCU}" --freq "${F_CPU}"
