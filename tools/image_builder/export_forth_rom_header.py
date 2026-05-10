from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FORTH_DIR = REPO_ROOT / "tools" / "forth"
ASSEMBLER_DIR = FORTH_DIR / "Assembler"
ASSEMBLY_SCRIPT = ASSEMBLER_DIR / "eForth.asm.py"
OUTPUT_HEADER = REPO_ROOT / "firmware" / "mega" / "pdr_vm" / "generated" / "pdr16_at_forth_image.h"


def read_split_rom() -> list[int]:
    low_path = ASSEMBLER_DIR / "eForth_lo.bin"
    high_path = ASSEMBLER_DIR / "eForth_hi.bin"
    low = low_path.read_bytes()
    high = high_path.read_bytes()
    if len(low) != len(high):
        raise RuntimeError("Split ROM byte streams differ in length.")
    return [low[index] | (high[index] << 8) for index in range(len(low))]


def render_header(words: list[int]) -> str:
    chunk_words = 8192
    chunk_count = (len(words) + chunk_words - 1) // chunk_words
    lines: list[str] = []
    lines.append("#ifndef PDR16_AT_FORTH_IMAGE_H")
    lines.append("#define PDR16_AT_FORTH_IMAGE_H")
    lines.append("")
    lines.append("#include <avr/pgmspace.h>")
    lines.append("#include <stdint.h>")
    lines.append("")
    lines.append(f"#define PDR16_AT_ROM_WORDS {len(words)}u")
    lines.append(f"#define PDR16_AT_ROM_CHUNK_WORDS {chunk_words}u")
    lines.append(f"#define PDR16_AT_ROM_CHUNK_COUNT {chunk_count}u")
    lines.append("")
    for chunk_index in range(chunk_count):
        start = chunk_index * chunk_words
        end = min(start + chunk_words, len(words))
        lines.append(
            f"static const uint16_t pdr16_at_forth_rom_chunk_{chunk_index}[{end - start}] PROGMEM = {{"
        )
        row: list[str] = []
        for index in range(start, end):
            row.append(f"0x{words[index]:04X}")
            if len(row) == 8 or index == end - 1:
                lines.append("    " + ", ".join(row) + ",")
                row = []
        lines.append("};")
        lines.append("")

    lines.append("static inline uint16_t pdr16_at_rom_read_word(uint16_t addr) {")
    lines.append("    const uint16_t chunk_index = addr / PDR16_AT_ROM_CHUNK_WORDS;")
    lines.append("    const uint16_t chunk_offset = addr % PDR16_AT_ROM_CHUNK_WORDS;")
    lines.append("    switch (chunk_index) {")
    for chunk_index in range(chunk_count):
        lines.append(f"        case {chunk_index}u:")
        lines.append(
            f"            return pgm_read_word_far(pgm_get_far_address(pdr16_at_forth_rom_chunk_{chunk_index}) + ((uint32_t)chunk_offset * 2u));"
        )
    lines.append("        default:")
    lines.append("            return 0xFFFFu;")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.append("#endif")
    lines.append("")
    return "\n".join(lines)


def build_rom() -> None:
    subprocess.run([sys.executable, str(ASSEMBLY_SCRIPT)], cwd=str(ASSEMBLER_DIR), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the copied Forth image and export an Arduino header.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Reuse the existing split ROM binaries instead of rebuilding them first.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_HEADER),
        help="Output header path.",
    )
    args = parser.parse_args()

    if not args.skip_build:
        build_rom()

    words = read_split_rom()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_header(words), encoding="ascii")
    print(f"Wrote {len(words)} ROM words to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
