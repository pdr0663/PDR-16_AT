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
SIMAVR_ARCHIVE="${SIMAVR_ARCHIVE:-}"
SIMAVR_NO_FETCH="${SIMAVR_NO_FETCH:-0}"
JOBS="${JOBS:-$(nproc 2>/dev/null || printf '2')}"

mkdir -p "${SIMAVR_PARENT}"

if [[ ! -d "${SIMAVR_ROOT}/.git" && ! -d "${SIMAVR_ROOT}/simavr" ]]; then
  if [[ -n "${SIMAVR_ARCHIVE}" ]]; then
    if [[ ! -f "${SIMAVR_ARCHIVE}" ]]; then
      echo "SIMAVR_ARCHIVE does not exist: ${SIMAVR_ARCHIVE}" >&2
      exit 1
    fi
    echo "Extracting ${SIMAVR_ARCHIVE} into ${SIMAVR_PARENT}"
    tmp_dir="$(mktemp -d)"
    trap 'rm -rf "${tmp_dir}"' EXIT
    tar -xf "${SIMAVR_ARCHIVE}" -C "${tmp_dir}"
    extracted="$(find "${tmp_dir}" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
    if [[ -z "${extracted}" ]]; then
      echo "Archive did not contain a top-level directory: ${SIMAVR_ARCHIVE}" >&2
      exit 1
    fi
    rm -rf "${SIMAVR_ROOT}"
    mv "${extracted}" "${SIMAVR_ROOT}"
  elif [[ "${SIMAVR_NO_FETCH}" == "1" ]]; then
    cat >&2 <<EOF
No simavr checkout exists at ${SIMAVR_ROOT}, and SIMAVR_NO_FETCH=1 was set.
Provide one of:
  SIMAVR_ARCHIVE=/path/to/simavr.tar.gz ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh
  SIMAVR_ROOT=/path/to/simavr ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh
EOF
    exit 1
  else
    echo "Cloning simavr into ${SIMAVR_ROOT}"
    git clone "${SIMAVR_REPO}" "${SIMAVR_ROOT}"
  fi
fi

if [[ -d "${SIMAVR_ROOT}/.git" && -n "${SIMAVR_REF}" && "${SIMAVR_NO_FETCH}" != "1" ]]; then
  git -C "${SIMAVR_ROOT}" fetch --tags origin "${SIMAVR_REF}" || true
  git -C "${SIMAVR_ROOT}" checkout "${SIMAVR_REF}"
elif [[ -d "${SIMAVR_ROOT}/.git" && -n "${SIMAVR_REF}" ]]; then
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
