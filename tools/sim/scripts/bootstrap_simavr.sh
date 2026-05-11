#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"

REPO_ROOT="$(simavr_repo_root)"
SIMAVR_PARENT="${SIMAVR_PARENT:-${REPO_ROOT}/avrsim}"
SIMAVR_ROOT="${SIMAVR_ROOT:-${SIMAVR_PARENT}/simavr}"
SIMAVR_REPO="${SIMAVR_REPO:-https://github.com/buserror/simavr.git}"
SIMAVR_REF="${SIMAVR_REF:-master}"
JOBS="${JOBS:-$(nproc 2>/dev/null || printf '2')}"

mkdir -p "${SIMAVR_PARENT}"

if [[ ! -d "${SIMAVR_ROOT}/.git" ]]; then
  echo "Cloning simavr into ${SIMAVR_ROOT}"
  git clone "${SIMAVR_REPO}" "${SIMAVR_ROOT}"
fi

if [[ -n "${SIMAVR_REF}" ]]; then
  git -C "${SIMAVR_ROOT}" fetch --tags origin "${SIMAVR_REF}" || true
  git -C "${SIMAVR_ROOT}" checkout "${SIMAVR_REF}"
fi

make -C "${SIMAVR_ROOT}/simavr" -j"${JOBS}"
make -C "${SIMAVR_ROOT}/examples/parts" -j"${JOBS}"

cat <<EOF2

simavr bootstrap complete.

Next steps:
  ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh
  ${REPO_ROOT}/tools/sim/scripts/run_mega_vm_pty.sh
EOF2
