#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/sim/scripts/simavr_env.sh
source "${SCRIPT_DIR}/simavr_env.sh"
REPO_ROOT="$(simavr_repo_root)"
DEFAULT_SOURCE="${REPO_ROOT}/tools/forth/Forth Sources/04-ansi.fs"
OUT_DIR="${OUT_DIR:-${REPO_ROOT}/tools/sim/out}"
PORT="${PORT:-/tmp/simavr-uart0}"
BAUD="${BAUD:-115200}"
STARTUP_DELAY_MS="${STARTUP_DELAY_MS:-1000}"
INTER_LINE_DELAY_MS="${INTER_LINE_DELAY_MS:-25}"
PROMPT_TIMEOUT_MS="${PROMPT_TIMEOUT_MS:-1500}"
PTY_WAIT_SEC="${PTY_WAIT_SEC:-10}"
BUILD_MODE="auto"
KEEP_SIM=0
SOURCES=()
SOURCE_LISTS=()

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Start the PTY-backed Mega VM simulator and feed repository Forth source files
through ${PORT}.  With no source options, this compiles:
  ${DEFAULT_SOURCE}

Options:
  --source <path>              Forth source file to send; may be repeated.
  --source-list <path>         File containing source paths; may be repeated.
  --out-dir <path>             Output directory for logs (default: ${OUT_DIR}).
  --port <path>                PTY/serial path (default: ${PORT}).
  --baud <rate>                Baud rate passed to sender (default: ${BAUD}).
  --startup-delay-ms <ms>      Sender startup delay (default: ${STARTUP_DELAY_MS}).
  --inter-line-delay-ms <ms>   Delay after each line (default: ${INTER_LINE_DELAY_MS}).
  --prompt-timeout-ms <ms>     Settled-output timeout (default: ${PROMPT_TIMEOUT_MS}).
  --pty-wait-sec <sec>         Wait for simulator PTY (default: ${PTY_WAIT_SEC}).
  --build                      Force rebuilding the PTY harness before running.
  --no-build                   Do not build the PTY harness; use the existing binary.
  --keep-sim                   Leave simulator running after the sender exits.
  -h, --help                   Show this help.

Useful examples:
  $(basename "$0")
  $(basename "$0") --source-list "${REPO_ROOT}/tools/forth/Forth Sources/build_order.txt"
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      [[ $# -ge 2 ]] || { echo "Missing value for --source" >&2; exit 2; }
      SOURCES+=("$2")
      shift 2
      ;;
    --source-list)
      [[ $# -ge 2 ]] || { echo "Missing value for --source-list" >&2; exit 2; }
      SOURCE_LISTS+=("$2")
      shift 2
      ;;
    --out-dir)
      [[ $# -ge 2 ]] || { echo "Missing value for --out-dir" >&2; exit 2; }
      OUT_DIR="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || { echo "Missing value for --port" >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    --baud)
      [[ $# -ge 2 ]] || { echo "Missing value for --baud" >&2; exit 2; }
      BAUD="$2"
      shift 2
      ;;
    --startup-delay-ms)
      [[ $# -ge 2 ]] || { echo "Missing value for --startup-delay-ms" >&2; exit 2; }
      STARTUP_DELAY_MS="$2"
      shift 2
      ;;
    --inter-line-delay-ms)
      [[ $# -ge 2 ]] || { echo "Missing value for --inter-line-delay-ms" >&2; exit 2; }
      INTER_LINE_DELAY_MS="$2"
      shift 2
      ;;
    --prompt-timeout-ms)
      [[ $# -ge 2 ]] || { echo "Missing value for --prompt-timeout-ms" >&2; exit 2; }
      PROMPT_TIMEOUT_MS="$2"
      shift 2
      ;;
    --pty-wait-sec)
      [[ $# -ge 2 ]] || { echo "Missing value for --pty-wait-sec" >&2; exit 2; }
      PTY_WAIT_SEC="$2"
      shift 2
      ;;
    --build)
      BUILD_MODE="always"
      shift
      ;;
    --no-build)
      BUILD_MODE="never"
      shift
      ;;
    --keep-sim)
      KEEP_SIM=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ${#SOURCES[@]} -eq 0 && ${#SOURCE_LISTS[@]} -eq 0 ]]; then
  SOURCES+=("${DEFAULT_SOURCE}")
fi

mkdir -p "${OUT_DIR}"
TRANSCRIPT="${OUT_DIR}/forth_compile_transcript.txt"
SIM_STDOUT="${OUT_DIR}/mega_vm_pty.stdout.txt"
SIM_STDERR="${OUT_DIR}/mega_vm_pty.stderr.txt"
RUN_LOG="${OUT_DIR}/compile_forth_sources.log"
SENDER="${REPO_ROOT}/tools/sim/send_forth_file.py"
RUNNER="${REPO_ROOT}/tools/sim/scripts/run_mega_vm_pty.sh"
BUILDER="${REPO_ROOT}/tools/sim/scripts/build_mega_vm_pty.sh"
HARNESS="${REPO_ROOT}/tools/sim/build/mega_vm_pty"
SIM_PID=""

cleanup() {
  local rc=$?
  if [[ -n "${SIM_PID}" && "${KEEP_SIM}" -eq 0 ]]; then
    kill "${SIM_PID}" 2>/dev/null || true
    wait "${SIM_PID}" 2>/dev/null || true
  fi
  return "${rc}"
}
trap cleanup EXIT

{
  echo "# compile_forth_sources.sh"
  date -u +"# started_utc=%Y-%m-%dT%H:%M:%SZ"
  echo "# repo=${REPO_ROOT}"
  echo "# port=${PORT}"
  echo "# transcript=${TRANSCRIPT}"
  for source in "${SOURCES[@]}"; do
    echo "# source=${source}"
  done
  for source_list in "${SOURCE_LISTS[@]}"; do
    echo "# source_list=${source_list}"
  done
} >"${RUN_LOG}"

if [[ -f "${HARNESS}" && ! -x "${HARNESS}" ]]; then
  chmod +x "${HARNESS}"
fi

NEEDS_BUILD=0
if [[ "${BUILD_MODE}" == "always" ]]; then
  NEEDS_BUILD=1
elif [[ "${BUILD_MODE}" == "auto" ]] && simavr_harness_needs_rebuild "${HARNESS}"; then
  NEEDS_BUILD=1
fi

if [[ "${NEEDS_BUILD}" -eq 1 ]]; then
  if ! "${BUILDER}" >>"${RUN_LOG}" 2>&1; then
    cat >&2 <<EOF
Failed to build the PTY harness. See:
  ${RUN_LOG}

If simavr is unavailable in this environment, install/build simavr first or run
with an existing harness and --no-build.
EOF
    exit 1
  fi
elif [[ ! -x "${HARNESS}" ]]; then
  cat >&2 <<EOF
PTY harness is not executable: ${HARNESS}
Build it with:
  ${BUILDER}
EOF
  exit 1
fi

rm -f "${PORT}"
"${RUNNER}" >"${SIM_STDOUT}" 2>"${SIM_STDERR}" &
SIM_PID=$!
echo "# sim_pid=${SIM_PID}" >>"${RUN_LOG}"

waited=0
while [[ ! -e "${PORT}" ]]; do
  if ! kill -0 "${SIM_PID}" 2>/dev/null; then
    echo "Simulator exited before creating ${PORT}." >&2
    echo "Simulator stdout: ${SIM_STDOUT}" >&2
    echo "Simulator stderr: ${SIM_STDERR}" >&2
    exit 1
  fi
  if [[ "${waited}" -ge "${PTY_WAIT_SEC}" ]]; then
    echo "Timed out waiting for ${PORT}." >&2
    echo "Simulator stdout: ${SIM_STDOUT}" >&2
    echo "Simulator stderr: ${SIM_STDERR}" >&2
    exit 1
  fi
  sleep 1
  waited=$((waited + 1))
done

echo "# pty_ready_after_sec=${waited}" >>"${RUN_LOG}"

sender_args=(
  "${SENDER}"
  --port "${PORT}"
  --baud "${BAUD}"
  --startup-delay-ms "${STARTUP_DELAY_MS}"
  --inter-line-delay-ms "${INTER_LINE_DELAY_MS}"
  --prompt-timeout-ms "${PROMPT_TIMEOUT_MS}"
  --log "${TRANSCRIPT}"
)
for source in "${SOURCES[@]}"; do
  sender_args+=(--source "${source}")
done
for source_list in "${SOURCE_LISTS[@]}"; do
  sender_args+=(--source-list "${source_list}")
done

python3 "${sender_args[@]}" 2>&1 | tee -a "${RUN_LOG}"
