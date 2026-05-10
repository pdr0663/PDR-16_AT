from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VM_CONFIG_PATH = REPO_ROOT / "firmware" / "mega" / "pdr_vm" / "vm_config.h"
ELF_PATH = REPO_ROOT / "firmware" / "mega" / "pdr_vm" / ".build-cli" / "pdr_vm.ino.elf"
HEX_PATH = REPO_ROOT / "firmware" / "mega" / "pdr_vm" / ".build-cli" / "pdr_vm.ino.hex"
ROM_HEADER_PATH = REPO_ROOT / "firmware" / "mega" / "pdr_vm" / "generated" / "pdr16_at_forth_image.h"
ROM_LOW_PATH = REPO_ROOT / "tools" / "forth" / "Assembler" / "eForth_lo.bin"
ROM_HIGH_PATH = REPO_ROOT / "tools" / "forth" / "Assembler" / "eForth_hi.bin"


DEFINE_RE = re.compile(r"^\s*#define\s+(\w+)\s+(.+?)\s*$", re.MULTILINE)
UINT_SUFFIX_RE = re.compile(r"(?<=\w)(?:ul|u)\b", re.IGNORECASE)
WORD_COUNT_RE = re.compile(r"^\s*#define\s+PDR16_AT_ROM_WORDS\s+(\d+)u\s*$", re.MULTILINE)
CHUNK_COUNT_RE = re.compile(r"^\s*#define\s+PDR16_AT_ROM_CHUNK_COUNT\s+(\d+)u\s*$", re.MULTILINE)


def _load_defines() -> dict[str, str]:
    text = VM_CONFIG_PATH.read_text(encoding="ascii")
    return {name: value for name, value in DEFINE_RE.findall(text) if name.startswith("VM_")}


def _eval_define(name: str, defines: dict[str, str], cache: dict[str, int], visiting: set[str]) -> int:
    if name in cache:
        return cache[name]
    if name in visiting:
        raise RuntimeError(f"Cyclic define dependency while resolving {name}.")
    visiting.add(name)
    expr = defines[name]
    normalized = UINT_SUFFIX_RE.sub("", expr)
    for other_name in sorted(defines, key=len, reverse=True):
        if other_name == name or not re.search(rf"\b{re.escape(other_name)}\b", normalized):
            continue
        replacement = str(_eval_define(other_name, defines, cache, visiting))
        normalized = re.sub(rf"\b{re.escape(other_name)}\b", replacement, normalized)
    cache[name] = int(eval(normalized, {"__builtins__": {}}, {}))
    visiting.remove(name)
    return cache[name]


def _read_rom_header_metadata() -> tuple[int, int]:
    text = ROM_HEADER_PATH.read_text(encoding="ascii")
    rom_words_match = WORD_COUNT_RE.search(text)
    chunk_count_match = CHUNK_COUNT_RE.search(text)
    if rom_words_match is None or chunk_count_match is None:
        raise RuntimeError("ROM header is missing expected metadata defines.")
    return int(rom_words_match.group(1)), int(chunk_count_match.group(1))


def build_manifest() -> dict[str, object]:
    defines = _load_defines()
    cache: dict[str, int] = {}
    resolved = {name: _eval_define(name, defines, cache, set()) for name in defines}
    rom_words, rom_chunk_count = _read_rom_header_metadata()

    low_size = ROM_LOW_PATH.stat().st_size
    high_size = ROM_HIGH_PATH.stat().st_size
    if low_size != high_size:
        raise RuntimeError("Split ROM byte streams differ in length.")

    return {
        "project": "PDR-16_AT",
        "target": {
            "mcu": "atmega2560",
            "fqbn": "arduino:avr:mega",
            "clock_hz": 16_000_000,
            "serial": {
                "device": "UART0 / Arduino Serial",
                "baud": resolved["VM_BAUD_RATE"],
            },
        },
        "artifacts": {
            "simulator_input_preferred": str(ELF_PATH),
            "simulator_input_fallback": str(HEX_PATH),
            "forth_rom_header": str(ROM_HEADER_PATH),
            "forth_rom_low_bytes": str(ROM_LOW_PATH),
            "forth_rom_high_bytes": str(ROM_HIGH_PATH),
            "elf_exists": ELF_PATH.exists(),
            "hex_exists": HEX_PATH.exists(),
        },
        "rom": {
            "logical_word_start": resolved["VM_ROM_START"],
            "logical_word_end": resolved["VM_ROM_END"],
            "word_count": rom_words,
            "chunk_count": rom_chunk_count,
            "split_byte_count_per_plane": low_size,
        },
        "ram": {
            "regions": [
                {
                    "name": "low_ram",
                    "logical_word_start": resolved["VM_RAM_LOW_START"],
                    "logical_word_end": resolved["VM_RAM_LOW_END"],
                    "word_count": resolved["VM_RAM_LOW_WORDS"],
                },
                {
                    "name": "high_ram",
                    "logical_word_start": resolved["VM_RAM_HIGH_START"],
                    "logical_word_end": resolved["VM_RAM_HIGH_END"],
                    "word_count": resolved["VM_RAM_HIGH_WORDS"],
                },
            ],
            "dictionary_logical_start": resolved["VM_RAM_LOW_START"],
            "stack_empty": {
                "data": resolved["VM_SP_EMPTY"],
                "return": resolved["VM_RP_EMPTY"],
            },
            "stack_write_floors": {
                "data": resolved["VM_DATA_STACK_WRITE_FLOOR"],
                "return": resolved["VM_RETURN_STACK_WRITE_FLOOR"],
            },
            "user_pointer": resolved["VM_UPP"],
        },
        "execution": {
            "cold_vector": resolved["VM_COLD_VECTOR"],
            "step_budget": resolved["VM_STEP_BUDGET"],
            "notes": [
                "The current VM keeps logical RAM in C arrays rather than AVR SRAM-mirrored addresses.",
                "The simulator must preserve Serial RX/TX behavior because ?KEY and EMIT are bound to UART-backed primitives.",
                "The initial runtime dictionary begins at logical word address 0x8000 and spans two discontiguous RAM regions.",
            ],
        },
        "capture_contract": {
            "primary_goal": "Capture post-seed dictionary contents after compiling a Forth library under the Mega VM.",
            "minimum_needed": [
                "UART console transcript for command/control",
                "Logical RAM words from dictionary-bearing regions",
                "Final values of CP/HERE-related dictionary pointers from VM-visible memory",
            ],
            "reference_modules_precompiled_on_host": [
                "03-fstrings.fs",
                "04-ansi.fs",
                "07-math.fs",
                "08-editor.fs",
            ],
        },
    }


def main() -> int:
    manifest = build_manifest()
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
