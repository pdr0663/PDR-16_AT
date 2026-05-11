#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"
REPO_ROOT="$(simavr_repo_root)"
ROOT="$(simavr_default_root)"
HARNESS="${REPO_ROOT}/tools/sim/build/mega_vm_pty"

echo "simavr diagnostics"
echo "==================="
echo "repo root:          ${REPO_ROOT}"
echo "SIMAVR_ROOT:        ${ROOT}"
echo "simavr CLI:         $(simavr_find_cli 2>/dev/null || true)"
echo "simavr headers:     $(simavr_find_header_dir 2>/dev/null || true)"
echo "parts headers:      $(simavr_find_parts_header_dir 2>/dev/null || true)"
echo "simavr lib dir:     $(simavr_find_lib_dir 2>/dev/null || true)"
echo "parts lib dir:      $(simavr_find_parts_lib_dir 2>/dev/null || true)"
echo "library path:       $(simavr_library_path 2>/dev/null || true)"
echo

echo "required files"
echo "--------------"
SIM_INC="$(simavr_find_header_dir 2>/dev/null || true)"
PARTS_INC="$(simavr_find_parts_header_dir 2>/dev/null || true)"
SIM_LIB="$(simavr_find_lib_dir 2>/dev/null || true)"
PARTS_LIB="$(simavr_find_parts_lib_dir 2>/dev/null || true)"
check_file() {
  local label="$1"
  local dir="$2"
  local file="$3"
  if [[ -z "${dir}" ]]; then
    echo "missing: ${label} (${file}; no directory discovered)"
  elif [[ -e "${dir}/${file}" ]]; then
    echo "present: ${dir}/${file}"
  else
    echo "missing: ${dir}/${file}"
  fi
}
check_file "simavr header" "${SIM_INC}" sim_avr.h
check_file "simavr header" "${SIM_INC}" sim_elf.h
check_file "simavr header" "${SIM_INC}" sim_hex.h
check_file "parts header" "${PARTS_INC}" uart_pty.h
check_file "simavr library" "${SIM_LIB}" libsimavr.so
check_file "simavr library" "${SIM_LIB}" libsimavr.so.1
check_file "simavr library" "${SIM_LIB}" libsimavr.a
check_file "parts library" "${PARTS_LIB}" libsimavrparts.so
check_file "parts library" "${PARTS_LIB}" libsimavrparts.so.1
check_file "parts library" "${PARTS_LIB}" libsimavrparts.a

echo
if [[ -e "${HARNESS}" ]]; then
  echo "harness ldd"
  echo "-----------"
  ldd "${HARNESS}" 2>&1 || true
else
  echo "harness missing: ${HARNESS}"
fi

echo
cat <<EOF
setup options
-------------
1. Repo-local checkout/build, when GitHub is reachable:
     ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh
     ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh

2. Local archive supplied by the user or another machine:
     SIMAVR_ARCHIVE=/path/to/simavr.tar.gz ${REPO_ROOT}/tools/sim/scripts/bootstrap_simavr.sh
     ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh

3. System package install, when apt is reachable:
     apt-get update
     apt-get install -y simavr libsimavr-dev
     ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh

4. Explicit prebuilt paths:
     SIMAVR_INCLUDE_DIR=/path/to/simavr/sim \\
     SIMAVR_PARTS_INCLUDE_DIR=/path/to/examples/parts \\
     SIMAVR_LIB_DIR=/path/to/simavr/obj-x86_64-linux-gnu \\
     SIMAVR_PARTS_LIB_DIR=/path/to/examples/parts/obj-x86_64-linux-gnu \\
     ${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh
EOF
