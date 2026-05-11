#!/usr/bin/env bash
# Shared discovery helpers for the repo-local/system simavr workflow.

simavr_repo_root() {
  local script_dir repo_root
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  repo_root="$(cd "${script_dir}/../../.." && pwd)"
  printf '%s\n' "${repo_root}"
}

simavr_default_root() {
  local repo_root
  repo_root="$(simavr_repo_root)"
  if [[ -n "${SIMAVR_ROOT:-}" ]]; then
    printf '%s\n' "${SIMAVR_ROOT}"
  elif [[ -d "${repo_root}/avrsim/simavr/simavr" ]]; then
    printf '%s\n' "${repo_root}/avrsim/simavr"
  elif [[ -d "${repo_root}/avrsim/simavr" ]]; then
    printf '%s\n' "${repo_root}/avrsim"
  elif [[ -d "/mnt/c/Users/Paul/simavr/simavr" ]]; then
    printf '%s\n' "/mnt/c/Users/Paul/simavr"
  else
    printf '%s\n' "${repo_root}/avrsim/simavr"
  fi
}

simavr_find_obj_dir() {
  local base_dir="$1"
  if [[ ! -d "${base_dir}" ]]; then
    return 0
  fi
  find "${base_dir}" -maxdepth 1 -type d -name 'obj-*' -print 2>/dev/null | sort | head -n 1
}

simavr_first_existing_dir() {
  local candidate
  for candidate in "$@"; do
    if [[ -n "${candidate}" && -d "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  return 1
}

simavr_find_header_dir() {
  local root
  root="$(simavr_default_root)"
  simavr_first_existing_dir \
    "${SIMAVR_INCLUDE_DIR:-}" \
    "${root}/simavr/sim" \
    "${root}/include/simavr" \
    "/usr/local/include/simavr" \
    "/usr/local/include" \
    "/usr/include/simavr" \
    "/usr/include"
}

simavr_find_parts_header_dir() {
  local root
  root="$(simavr_default_root)"
  simavr_first_existing_dir \
    "${SIMAVR_PARTS_INCLUDE_DIR:-}" \
    "${root}/examples/parts" \
    "${root}/include/simavr" \
    "/usr/local/include/simavr" \
    "/usr/local/include" \
    "/usr/include/simavr" \
    "/usr/include"
}

simavr_find_lib_dir() {
  local root obj_dir candidate
  root="$(simavr_default_root)"
  obj_dir="$(simavr_find_obj_dir "${root}/simavr" || true)"
  for candidate in \
    "${SIMAVR_LIB_DIR:-}" \
    "${obj_dir}" \
    "/usr/local/lib" \
    "/usr/lib/$(gcc -dumpmachine 2>/dev/null || true)" \
    "/usr/lib/x86_64-linux-gnu" \
    "/usr/lib"; do
    if [[ -n "${candidate}" && -d "${candidate}" && ( -e "${candidate}/libsimavr.so" || -e "${candidate}/libsimavr.so.1" || -e "${candidate}/libsimavr.a" ) ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  return 1
}

simavr_find_parts_lib_dir() {
  local root obj_dir candidate
  root="$(simavr_default_root)"
  obj_dir="$(simavr_find_obj_dir "${root}/examples/parts" || true)"
  for candidate in \
    "${SIMAVR_PARTS_LIB_DIR:-}" \
    "${obj_dir}" \
    "/usr/local/lib" \
    "/usr/lib/$(gcc -dumpmachine 2>/dev/null || true)" \
    "/usr/lib/x86_64-linux-gnu" \
    "/usr/lib"; do
    if [[ -n "${candidate}" && -d "${candidate}" && ( -e "${candidate}/libsimavrparts.so" || -e "${candidate}/libsimavrparts.so.1" || -e "${candidate}/libsimavrparts.a" ) ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  return 1
}

simavr_find_cli() {
  local repo_root root obj_dir
  repo_root="$(simavr_repo_root)"
  if [[ -n "${SIMAVR_BIN:-}" ]]; then
    printf '%s\n' "${SIMAVR_BIN}"
    return 0
  fi

  root="$(simavr_default_root)"
  obj_dir="$(simavr_find_obj_dir "${root}/simavr" || true)"
  if [[ -n "${obj_dir}" && -x "${obj_dir}/simavr" ]]; then
    printf '%s\n' "${obj_dir}/simavr"
    return 0
  fi

  if command -v simavr >/dev/null 2>&1; then
    command -v simavr
    return 0
  fi

  printf '%s\n' "${repo_root}/avrsim/simavr/simavr/obj-*/simavr"
  return 1
}

simavr_library_path() {
  local sim_lib parts_lib
  sim_lib="$(simavr_find_lib_dir || true)"
  parts_lib="$(simavr_find_parts_lib_dir || true)"
  if [[ -n "${sim_lib}" && -n "${parts_lib}" && "${sim_lib}" != "${parts_lib}" ]]; then
    printf '%s:%s\n' "${parts_lib}" "${sim_lib}"
  elif [[ -n "${sim_lib}" ]]; then
    printf '%s\n' "${sim_lib}"
  elif [[ -n "${parts_lib}" ]]; then
    printf '%s\n' "${parts_lib}"
  fi
}

simavr_harness_needs_rebuild() {
  local harness="$1"
  if [[ ! -x "${harness}" ]]; then
    return 0
  fi
  if command -v ldd >/dev/null 2>&1 && ldd "${harness}" 2>/dev/null | grep -q 'not found'; then
    return 0
  fi
  return 1
}
