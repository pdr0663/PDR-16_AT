#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SIMAVR_BIN="${SIMAVR_BIN:-simavr}"
ELF_PATH="${ELF_PATH:-${REPO_ROOT}/firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf}"
MCU="${MCU:-atmega2560}"
F_CPU="${F_CPU:-16000000}"

if [[ ! -f "${ELF_PATH}" ]]; then
  echo "ELF not found: ${ELF_PATH}" >&2
  exit 1
fi

exec "${SIMAVR_BIN}" -m "${MCU}" -f "${F_CPU}" "${ELF_PATH}"
