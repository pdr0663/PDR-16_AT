#!/usr/bin/env bash
set -euo pipefail

UART_PATH="${UART_PATH:-/tmp/simavr-uart0}"
BAUD="${BAUD:-115200}"

if [[ ! -e "${UART_PATH}" ]]; then
  echo "UART path not found: ${UART_PATH}" >&2
  echo "Expected a PTY-backed simavr wrapper to create it first." >&2
  exit 1
fi

exec picocom -b "${BAUD}" "${UART_PATH}"
