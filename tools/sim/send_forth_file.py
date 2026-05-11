#!/usr/bin/env python3
"""Send Forth source files to a POSIX serial port or PTY.

This is the Linux/WSL counterpart to tools/forth/send_forth_file.ps1.  It is
intended for the simavr UART PTY (/tmp/simavr-uart0), but keeps baud-rate and
termios configuration flags so the same policy can also be used with a real
serial device.
"""

from __future__ import annotations

import argparse
import os
import re
import select
import sys
import termios
import time
import tty
from pathlib import Path
from typing import Iterable, TextIO

FAULT_RE = re.compile(r"VM fault|fault\s+\d+", re.IGNORECASE)
QUIET_AFTER_DATA_MS = 120
READ_CHUNK_SIZE = 4096

BAUD_RATES = {
    50: termios.B50,
    75: termios.B75,
    110: termios.B110,
    134: termios.B134,
    150: termios.B150,
    200: termios.B200,
    300: termios.B300,
    600: termios.B600,
    1200: termios.B1200,
    1800: termios.B1800,
    2400: termios.B2400,
    4800: termios.B4800,
    9600: termios.B9600,
    19200: termios.B19200,
    38400: termios.B38400,
}

for _rate_name in ("B57600", "B115200", "B230400", "B460800", "B500000", "B576000", "B921600"):
    if hasattr(termios, _rate_name):
        BAUD_RATES[int(_rate_name[1:])] = getattr(termios, _rate_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send Forth source files line-by-line to a POSIX serial port or simavr PTY.",
    )
    parser.add_argument(
        "--port",
        default="/tmp/simavr-uart0",
        help="serial device or PTY path (default: %(default)s)",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="baud rate for real serial devices; PTYs ignore it (default: %(default)s)",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        type=Path,
        help="Forth source file to send; may be repeated",
    )
    parser.add_argument(
        "--source-list",
        type=Path,
        help=(
            "file containing source paths, one per line; relative entries are "
            "resolved from the list file's directory"
        ),
    )
    parser.add_argument(
        "--inter-line-delay-ms",
        type=int,
        default=25,
        help="delay after writing each line before reading output (default: %(default)s)",
    )
    parser.add_argument(
        "--prompt-timeout-ms",
        type=int,
        default=1500,
        help="maximum time to wait for settled output after each line (default: %(default)s)",
    )
    parser.add_argument(
        "--startup-delay-ms",
        type=int,
        default=250,
        help="delay after opening the port before draining startup output (default: %(default)s)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        help="write a complete send/receive transcript to this file",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="source-file text encoding (default: %(default)s)",
    )
    parser.add_argument(
        "--echo-source",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="include sent source lines in the transcript (default: true)",
    )
    args = parser.parse_args()
    if not args.source and args.source_list is None:
        parser.error("at least one --source or --source-list is required")
    if args.inter_line_delay_ms < 0:
        parser.error("--inter-line-delay-ms must be non-negative")
    if args.prompt_timeout_ms <= 0:
        parser.error("--prompt-timeout-ms must be positive")
    if args.startup_delay_ms < 0:
        parser.error("--startup-delay-ms must be non-negative")
    return args


def source_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = list(args.source)
    if args.source_list is not None:
        list_dir = args.source_list.resolve().parent
        for raw_line in args.source_list.read_text(encoding=args.encoding).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            path = Path(line)
            if not path.is_absolute():
                path = list_dir / path
            paths.append(path)
    return [path.resolve() for path in paths]


def configure_port(fd: int, baud: int) -> list:
    original_attrs = termios.tcgetattr(fd)
    tty.setraw(fd, termios.TCSANOW)
    attrs = termios.tcgetattr(fd)
    speed = BAUD_RATES.get(baud)
    if speed is None:
        raise ValueError(f"Unsupported baud rate for termios: {baud}")
    attrs[4] = speed
    attrs[5] = speed
    attrs[2] |= termios.CLOCAL | termios.CREAD
    attrs[2] &= ~termios.CSIZE
    attrs[2] |= termios.CS8
    attrs[2] &= ~(termios.PARENB | termios.CSTOPB)
    if hasattr(termios, "CRTSCTS"):
        attrs[2] &= ~termios.CRTSCTS
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return original_attrs


def decode_output(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def display_text(text: str) -> str:
    return text.replace("\r", r"\r").replace("\n", r"\n" + "\n")


def log_line(log: TextIO | None, line: str) -> None:
    if log is not None:
        log.write(line)
        if not line.endswith("\n"):
            log.write("\n")
        log.flush()


def read_available(fd: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        ready, _, _ = select.select([fd], [], [], 0)
        if not ready:
            break
        try:
            chunk = os.read(fd, READ_CHUNK_SIZE)
        except BlockingIOError:
            break
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def read_until_settled(fd: int, timeout_ms: int) -> bytes:
    deadline = time.monotonic() + timeout_ms / 1000.0
    quiet_deadline: float | None = None
    chunks: list[bytes] = []

    while time.monotonic() < deadline:
        now = time.monotonic()
        timeout = max(0.0, min(0.01, deadline - now))
        ready, _, _ = select.select([fd], [], [], timeout)
        if ready:
            try:
                chunk = os.read(fd, READ_CHUNK_SIZE)
            except BlockingIOError:
                chunk = b""
            if chunk:
                chunks.append(chunk)
                quiet_deadline = time.monotonic() + QUIET_AFTER_DATA_MS / 1000.0
                continue
        if quiet_deadline is not None and time.monotonic() >= quiet_deadline:
            break

    return b"".join(chunks)


def write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        _, writable, _ = select.select([], [fd], [])
        if not writable:
            continue
        written = os.write(fd, view)
        if written == 0:
            raise RuntimeError("Serial write returned zero bytes.")
        view = view[written:]


def iter_source_lines(path: Path, encoding: str) -> Iterable[str]:
    with path.open("r", encoding=encoding, newline=None) as source:
        for line in source:
            yield line.rstrip("\r\n")


def send_sources(fd: int, paths: list[Path], args: argparse.Namespace, log: TextIO | None) -> None:
    for source_index, path in enumerate(paths, start=1):
        if not path.is_file():
            raise FileNotFoundError(f"Source file not found: {path}")
        header = f"Sending {path} to {args.port} at {args.baud} baud"
        print(header)
        log_line(log, f"\n# source {source_index}: {path}")

        for line_number, line in enumerate(iter_source_lines(path, args.encoding), start=1):
            if args.echo_source:
                log_line(log, f"> {path}:{line_number}: {line}")
            write_all(fd, line.encode(args.encoding) + b"\r")
            if args.inter_line_delay_ms:
                time.sleep(args.inter_line_delay_ms / 1000.0)

            response = read_until_settled(fd, args.prompt_timeout_ms)
            if response:
                text = decode_output(response)
                log_line(log, text)
                print(f"[{path.name}:{line_number}] {display_text(text)}")
                if FAULT_RE.search(text):
                    raise RuntimeError(f"Target reported a VM fault after {path}:{line_number}.")


def main() -> int:
    args = parse_args()
    paths = source_paths(args)
    log: TextIO | None = None
    fd: int | None = None
    original_attrs: list | None = None

    try:
        if args.log is not None:
            args.log.parent.mkdir(parents=True, exist_ok=True)
            log = args.log.open("w", encoding="utf-8")
            log_line(log, f"# port: {args.port}")
            log_line(log, f"# baud: {args.baud}")
            for path in paths:
                log_line(log, f"# queued-source: {path}")

        fd = os.open(args.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        original_attrs = configure_port(fd, args.baud)
        if args.startup_delay_ms:
            time.sleep(args.startup_delay_ms / 1000.0)
        startup = read_available(fd)
        if startup:
            text = decode_output(startup)
            log_line(log, "# startup output")
            log_line(log, text)
            print(f"[startup] {display_text(text)}")
            if FAULT_RE.search(text):
                raise RuntimeError("Target reported a VM fault during startup output.")

        send_sources(fd, paths, args, log)
        trailing = read_available(fd)
        if trailing:
            text = decode_output(trailing)
            log_line(log, "# trailing output")
            log_line(log, text)
            print(f"[trailing] {display_text(text)}")
            if FAULT_RE.search(text):
                raise RuntimeError("Target reported a VM fault in trailing output.")
        return 0
    except Exception as exc:  # argparse has already handled usage errors.
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        if fd is not None:
            if original_attrs is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSANOW, original_attrs)
                except termios.error:
                    pass
            os.close(fd)
        if log is not None:
            log.close()


if __name__ == "__main__":
    raise SystemExit(main())
