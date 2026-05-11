#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BIN_PATH="${BIN_PATH:-${REPO_ROOT}/tools/sim/build/mega_vm_pty}"
FIRMWARE_PATH="${FIRMWARE_PATH:-${REPO_ROOT}/firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex}"
MCU="${MCU:-atmega2560}"
F_CPU="${F_CPU:-16000000}"

if [[ ! -x "${BIN_PATH}" ]]; then
  echo "PTY harness not found: ${BIN_PATH}" >&2
  echo "Build it first with ./build_mega_vm_pty.sh" >&2
  exit 1
fi

if [[ ! -f "${FIRMWARE_PATH}" ]]; then
  echo "Firmware not found: ${FIRMWARE_PATH}" >&2
  exit 1
fi

exec "${BIN_PATH}" --firmware "${FIRMWARE_PATH}" --mcu "${MCU}" --freq "${F_CPU}"
