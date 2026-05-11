#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"
REPO_ROOT="$(simavr_repo_root)"
if ! SIMAVR_BIN="$(simavr_find_cli)"; then
  echo "simavr executable not found." >&2
  echo "Run ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh or set SIMAVR_BIN." >&2
  exit 1
fi
ELF_PATH="${ELF_PATH:-${REPO_ROOT}/firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf}"
MCU="${MCU:-atmega2560}"
F_CPU="${F_CPU:-16000000}"

if [[ ! -f "${ELF_PATH}" ]]; then
  echo "ELF not found: ${ELF_PATH}" >&2
  exit 1
fi

exec "${SIMAVR_BIN}" -m "${MCU}" -f "${F_CPU}" "${ELF_PATH}"
