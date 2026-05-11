#!/usr/bin/env bash
# Shared discovery helpers for the repo-local simavr/avrsim workflow.

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
