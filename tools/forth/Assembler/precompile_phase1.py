from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal


ASSEMBLER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ASSEMBLER_DIR.parent
FORTH_SOURCE_DIR = PROJECT_DIR / "Forth Sources"
GENERATED_DIR = ASSEMBLER_DIR / "generated_forth"


@dataclass(frozen=True)
class ModuleSpec:
    source_name: str
    generated_name: str
    emitter_name: str
    allowed_tokens: frozenset[str] | None = None


PHASE1_MODULES = [
    ModuleSpec("03-fstrings.fs", "precompiled_03_fstrings.py", "emit_precompiled_03_fstrings"),
    ModuleSpec("04-ansi.fs", "precompiled_04_ansi.py", "emit_precompiled_04_ansi"),
    ModuleSpec("07-math.fs", "precompiled_07_math.py", "emit_precompiled_07_math"),
    ModuleSpec("08-editor.fs", "precompiled_08_editor.py", "emit_precompiled_08_editor"),
]


CREATE_ALLOT_RE = re.compile(r"^CREATE\s+(\S+)\s+(\d+)\s+ALLOT\s*$")
CREATE_RE = re.compile(r"^CREATE\s+(\S+)\s*$")
STRING_COPY_RE = re.compile(r'^S"\s*(.*?)"\s+(\S+)\s+(-?\d+)\s+\+\s+SWAP\s+CMOVE\s*$')
NUMBER_RE = re.compile(r"^[+-]?\d+$")
USER_DEF_RE = re.compile(r"^(.*?)\bUSER\s+(\S+)\s*$")
QUALIFIER_TOKENS = {"PRIVATE", "COMPILE-ONLY", "IMMEDIATE"}


@dataclass
class EmittedEntry:
    name: str
    kind: Literal["colon", "variable", "user"]
    body_lines: list[str]
    public: bool = True
    immediate: bool = False
    compile_only: bool = False


def ensure_phase1_generated() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    init_path = GENERATED_DIR / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    script_mtime = Path(__file__).stat().st_mtime
    for spec in PHASE1_MODULES:
        source_path = FORTH_SOURCE_DIR / spec.source_name
        generated_path = GENERATED_DIR / spec.generated_name
        if (
            not generated_path.exists()
            or generated_path.stat().st_mtime < source_path.stat().st_mtime
            or generated_path.stat().st_mtime < script_mtime
        ):
            _write_generated_module(spec)


def _write_generated_module(spec: ModuleSpec) -> None:
    source_path = FORTH_SOURCE_DIR / spec.source_name
    text = _render_module(source_path, spec.emitter_name, allowed_tokens=spec.allowed_tokens)
    (GENERATED_DIR / spec.generated_name).write_text(text, encoding="utf-8")


def _module_header(source_path: Path, emitter_name: str) -> list[str]:
    rel = source_path.relative_to(PROJECT_DIR.parent).as_posix()
    return [
        "import asm",
        "from asm import colon, comment, ds, dw, label, skip_user, user, variable",
        "",
        "",
        f"def {emitter_name}() -> None:",
        f"    comment('precompiled from {rel}')",
    ]


def _render_module(
    source_path: Path,
    emitter_name: str,
    allowed_tokens: frozenset[str] | None = None,
) -> str:
    lines = _module_header(source_path, emitter_name)
    entries: list[EmittedEntry] = []
    pending: list[str] = []
    current_table: str | None = None
    current_values: list[int] = []
    current_base = 10
    simple_constants: dict[str, int] = {}

    def flush_table() -> None:
        nonlocal current_table, current_values
        if current_table is None:
            return
        entries.append(
            EmittedEntry(
                name=current_table,
                kind="variable",
                body_lines=_emit_variable_block(current_table, current_values),
            )
        )
        current_table = None
        current_values = []

    def apply_qualifier(qualifier: str) -> None:
        flush_table()
        if not entries:
            raise RuntimeError(f"Qualifier {qualifier!r} has no preceding definition in {source_path.name}")
        entry = entries[-1]
        if qualifier == "PRIVATE":
            entry.public = False
        elif qualifier == "COMPILE-ONLY":
            entry.compile_only = True
        elif qualifier == "IMMEDIATE":
            entry.immediate = True
        else:
            raise RuntimeError(f"Unsupported qualifier {qualifier!r} in {source_path.name}")

    for raw_line in source_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = raw_line.split("\\", 1)[0].strip()
        if not stripped or stripped.startswith("\\"):
            continue
        if stripped == ">BASE HEX":
            current_base = 16
            continue
        if stripped == "BASE>":
            current_base = 10
            continue
        if stripped in QUALIFIER_TOKENS:
            apply_qualifier(stripped)
            continue
        if pending:
            pending.append(stripped)
            if ";" not in stripped:
                continue
            stripped = " ".join(pending)
            pending = []
        elif stripped.startswith(":") and ";" not in stripped:
            pending = [stripped]
            continue

        create_allot_match = CREATE_ALLOT_RE.match(stripped)
        if create_allot_match is not None:
            flush_table()
            current_table = create_allot_match.group(1)
            current_values = [0] * int(create_allot_match.group(2))
            continue

        create_match = CREATE_RE.match(stripped)
        if create_match is not None:
            flush_table()
            current_table = create_match.group(1)
            current_values = []
            continue

        string_copy_match = STRING_COPY_RE.match(stripped)
        if string_copy_match is not None:
            text, target, offset_text = string_copy_match.groups()
            if current_table is None:
                raise RuntimeError(f"String copy without active CREATE in {source_path.name}: {stripped!r}")
            if target != current_table:
                raise RuntimeError(f"Unexpected table target in {source_path.name}: {stripped!r}")
            offset = int(offset_text, 10)
            for index, char in enumerate(text):
                current_values[offset + index] = ord(char)
            continue

        user_def_match = USER_DEF_RE.match(stripped)
        if user_def_match is not None:
            flush_table()
            expr_text, name = user_def_match.groups()
            offset = _eval_user_offset(expr_text.strip(), simple_constants, source_path.name)
            entries.append(
                EmittedEntry(
                    name=name,
                    kind="user",
                    body_lines=_emit_user_block(name, offset),
                )
            )
            continue

        colon_parts = _split_colon_definition(stripped)
        if colon_parts is None:
            if current_table is None:
                raise RuntimeError(f"Unsupported definition in {source_path.name}: {stripped!r}")
            current_values.extend(_parse_numeric_row(stripped, current_base))
            continue

        flush_table()
        name, body_text, qualifiers_text = colon_parts
        ops = _parse_colon_body(body_text or "", current_base)
        _validate_ops(source_path.name, name, ops, allowed_tokens)
        entry = EmittedEntry(
            name=name,
            kind="colon",
            body_lines=_emit_colon_block(name, ops, source_path.stem),
        )
        for qualifier in _parse_qualifiers(qualifiers_text):
            if qualifier == "PRIVATE":
                entry.public = False
            elif qualifier == "COMPILE-ONLY":
                entry.compile_only = True
            elif qualifier == "IMMEDIATE":
                entry.immediate = True
        entries.append(entry)
        constant_value = _extract_simple_constant(ops)
        if constant_value is not None:
            simple_constants[name] = constant_value

    if pending:
        raise RuntimeError(f"Unterminated colon definition in {source_path.name}: {' '.join(pending)!r}")
    flush_table()
    for entry in entries:
        lines.extend(_apply_entry_qualifiers(entry))
    lines.append("")
    return "\n".join(lines)


def _emit_variable_block(name: str, values: list[int]) -> list[str]:
    if not values:
        raise RuntimeError(f"Variable {name} has no data to emit.")
    rendered = [f"    variable({name!r}, {values[0]!r})"]
    rest = values[1:]
    row_width = 16
    for start in range(0, len(rest), row_width):
        chunk = rest[start:start + row_width]
        rendered.append(f"    dw({chunk!r})")
    return rendered


def _emit_user_block(name: str, offset: int) -> list[str]:
    return [
        f"    if asm._USER < {offset} * asm.CELLL:",
        f"        skip_user({offset} - (asm._USER // asm.CELLL))",
        f"    elif asm._USER > {offset} * asm.CELLL:",
        f"        raise RuntimeError('USER offset overlap for {name}')",
        f"    user({name!r})",
    ]


def _apply_entry_qualifiers(entry: EmittedEntry) -> list[str]:
    if entry.kind == "user":
        if not entry.public or entry.immediate or entry.compile_only:
            raise RuntimeError(f"USER entry {entry.name} cannot be qualified.")
        return entry.body_lines

    if entry.kind != "colon":
        if entry.immediate or entry.compile_only:
            raise RuntimeError(f"Non-colon entry {entry.name} cannot be IMMEDIATE or COMPILE-ONLY.")
        if entry.public:
            return entry.body_lines
        first = entry.body_lines[0]
        return [first[:-1] + ", public=False)"] + entry.body_lines[1:]

    first = entry.body_lines[0]
    qualifier_parts: list[str] = []
    if not entry.public:
        qualifier_parts.append("public=False")
    if entry.immediate:
        qualifier_parts.append("immediate=True")
    if entry.compile_only:
        qualifier_parts.append("compile_only=True")
    if not qualifier_parts:
        return entry.body_lines
    return [first[:-1] + ", " + ", ".join(qualifier_parts) + ")"] + entry.body_lines[1:]


def _emit_colon_block(name: str, ops: list[tuple[str, object]], namespace: str) -> list[str]:
    rendered = [f"    colon({name!r}, [])"]
    pending: list[object] = []
    control_stack: list[tuple[str, str]] = []
    label_counter = 0

    def next_label(tag: str) -> str:
        nonlocal label_counter
        label_counter += 1
        safe_namespace = _encode_label_fragment(namespace)
        safe_name = _encode_label_fragment(name)
        return f"PC_{safe_namespace}_{safe_name}_{tag}_{label_counter}"

    def flush_pending() -> None:
        nonlocal pending
        if pending:
            rendered.append(f"    dw({pending!r})")
            pending = []

    for kind, payload in ops:
        if kind == "op":
            if payload == "RECURSE":
                pending.append(name)
                continue
            if payload == "BEGIN":
                flush_pending()
                begin_label = next_label("BEGIN")
                rendered.append(f"    label({begin_label!r})")
                control_stack.append(("begin", begin_label))
                continue
            if payload == "IF":
                false_label = next_label("IF_FALSE")
                pending.extend(["?branch", false_label])
                control_stack.append(("if", false_label))
                continue
            if payload == "ELSE":
                if_kind, if_label = control_stack.pop()
                if if_kind != "if":
                    raise RuntimeError(f"ELSE without matching IF in {name}")
                end_label = next_label("IF_END")
                pending.extend(["branch", end_label])
                flush_pending()
                rendered.append(f"    label({if_label!r})")
                control_stack.append(("else", end_label))
                continue
            if payload == "THEN":
                branch_kind, branch_label = control_stack.pop()
                if branch_kind not in {"if", "else"}:
                    raise RuntimeError(f"THEN without matching IF/ELSE in {name}")
                flush_pending()
                rendered.append(f"    label({branch_label!r})")
                continue
            if payload == "WHILE":
                begin_kind, begin_label = control_stack.pop()
                if begin_kind != "begin":
                    raise RuntimeError(f"WHILE without matching BEGIN in {name}")
                false_label = next_label("WHILE_END")
                pending.extend(["?branch", false_label])
                control_stack.append(("begin", begin_label))
                control_stack.append(("while", false_label))
                continue
            if payload == "AGAIN":
                begin_kind, begin_label = control_stack.pop()
                if begin_kind != "begin":
                    raise RuntimeError(f"AGAIN without matching BEGIN in {name}")
                pending.extend(["branch", begin_label])
                flush_pending()
                continue
            if payload == "REPEAT":
                while_kind, while_label = control_stack.pop()
                begin_kind, begin_label = control_stack.pop()
                if while_kind != "while" or begin_kind != "begin":
                    raise RuntimeError(f"REPEAT without matching BEGIN/WHILE in {name}")
                pending.extend(["branch", begin_label])
                flush_pending()
                rendered.append(f"    label({while_label!r})")
                continue
            if isinstance(payload, int):
                pending.extend(["doLIT", payload])
            elif isinstance(payload, str):
                pending.append(payload)
            else:
                raise RuntimeError(f"Unsupported payload in {name}: {payload!r}")
            continue
        flush_pending()
        ds_word, text = payload  # type: ignore[misc]
        rendered.append(f"    ds({ds_word!r}, {text!r})")

    if control_stack:
        raise RuntimeError(f"Unresolved control structure in {name}: {control_stack!r}")
    pending.append("EXIT")
    flush_pending()
    return rendered


def _extract_simple_constant(ops: list[tuple[str, object]]) -> int | None:
    if len(ops) != 1:
        return None
    kind, payload = ops[0]
    if kind != "op" or not isinstance(payload, int):
        return None
    return payload


def _eval_user_offset(expr_text: str, simple_constants: dict[str, int], source_name: str) -> int:
    if not expr_text:
        raise RuntimeError(f"Missing USER offset expression in {source_name}")

    stack: list[int] = []
    for token in expr_text.split():
        if NUMBER_RE.fullmatch(token):
            stack.append(int(token, 10))
        elif token in simple_constants:
            stack.append(simple_constants[token])
        elif token == "+":
            if len(stack) < 2:
                raise RuntimeError(f"Malformed USER offset expression in {source_name}: {expr_text!r}")
            rhs = stack.pop()
            lhs = stack.pop()
            stack.append(lhs + rhs)
        else:
            raise RuntimeError(f"Unsupported USER offset token {token!r} in {source_name}")

    if len(stack) != 1:
        raise RuntimeError(f"Malformed USER offset expression in {source_name}: {expr_text!r}")
    return stack[0]


def _parse_numeric_row(text: str, current_base: int) -> list[int]:
    values = []
    for part in text.split(","):
        token = part.strip()
        if not token:
            continue
        values.append(_parse_number(token, current_base))
    return values


def _parse_number(token: str, current_base: int) -> int:
    sign = -1 if token.startswith("-") else 1
    magnitude = token[1:] if token[:1] in "+-" else token
    return sign * int(magnitude, current_base)


def _parse_qualifiers(text: str | None) -> list[str]:
    if text is None:
        return []
    qualifiers = [token for token in text.split() if token]
    unknown = [token for token in qualifiers if token not in QUALIFIER_TOKENS]
    if unknown:
        raise RuntimeError(f"Unsupported qualifier tokens: {unknown!r}")
    return qualifiers


def _split_colon_definition(text: str) -> tuple[str, str, str] | None:
    if not text.startswith(":"):
        return None

    i = 1
    n = len(text)
    while i < n and text[i].isspace():
        i += 1
    if i >= n:
        raise RuntimeError(f"Malformed colon definition: {text!r}")

    name_start = i
    while i < n and not text[i].isspace():
        i += 1
    name = text[name_start:i]
    while i < n and text[i].isspace():
        i += 1
    body_start = i

    while i < n:
        if text.startswith('."', i):
            i = _skip_string_literal(text, i + 2, '."')
            continue
        if text.startswith('S"', i):
            i = _skip_string_literal(text, i + 2, 'S"')
            continue
        if text.startswith('ABORT"', i):
            i = _skip_string_literal(text, i + len('ABORT"'), 'ABORT"')
            continue
        if text[i] == ";":
            body = text[body_start:i].strip()
            qualifiers = text[i + 1 :].strip()
            return name, body, qualifiers
        i += 1

    raise RuntimeError(f"Unterminated colon definition: {text!r}")


def _skip_string_literal(text: str, i: int, token: str) -> int:
    n = len(text)
    if i < n and text[i] == " ":
        i += 1
    end = text.find('"', i)
    if end == -1:
        raise RuntimeError(f'Unterminated {token} string in {text!r}')
    return end + 1


def _encode_label_fragment(text: str) -> str:
    parts: list[str] = []
    for ch in text:
        if ch.isalnum() or ch == "_":
            parts.append(ch)
        else:
            parts.append(f"_{ord(ch):02X}")
    return "".join(parts)


def _validate_ops(
    source_name: str,
    word_name: str,
    ops: list[tuple[str, object]],
    allowed_tokens: frozenset[str] | None,
) -> None:
    if allowed_tokens is None:
        return
    for kind, payload in ops:
        if kind != "op":
            raise RuntimeError(f"Unsupported string form in constrained precompiled word {word_name} from {source_name}")
        if isinstance(payload, int):
            continue
        if payload not in allowed_tokens:
            raise RuntimeError(
                f"Token {payload!r} is outside the allowed precompiled vocabulary for {word_name} in {source_name}"
            )


def _parse_colon_body(body_text: str, current_base: int) -> list[tuple[str, object]]:
    ops: list[tuple[str, object]] = []
    i = 0
    n = len(body_text)
    while i < n:
        while i < n and body_text[i].isspace():
            i += 1
        if i >= n:
            break

        if body_text[i] == "(":
            end = body_text.find(")", i + 1)
            if end == -1:
                raise RuntimeError(f"Unterminated ( comment in {body_text!r}")
            i = end + 1
            continue

        if body_text.startswith('."', i):
            i += 2
            if i < n and body_text[i] == " ":
                i += 1
            end = body_text.find('"', i)
            if end == -1:
                raise RuntimeError(f'Unterminated ." string in {body_text!r}')
            ops.append(("string", ('."|', body_text[i:end])))
            i = end + 1
            continue

        if body_text.startswith('S"', i):
            i += 2
            if i < n and body_text[i] == " ":
                i += 1
            end = body_text.find('"', i)
            if end == -1:
                raise RuntimeError(f'Unterminated S" string in {body_text!r}')
            ops.append(("string", ('S"|', body_text[i:end])))
            i = end + 1
            continue

        if body_text.startswith('ABORT"', i):
            i += len('ABORT"')
            if i < n and body_text[i] == " ":
                i += 1
            end = body_text.find('"', i)
            if end == -1:
                raise RuntimeError(f'Unterminated ABORT" string in {body_text!r}')
            ops.append(("string", ('abort"', body_text[i:end])))
            i = end + 1
            continue

        start = i
        while i < n and not body_text[i].isspace():
            i += 1
        token = body_text[start:i]
        if NUMBER_RE.fullmatch(token) or (current_base == 16 and re.fullmatch(r"[+-]?[0-9A-F]+", token, re.IGNORECASE)):
            ops.append(("op", _parse_number(token, current_base)))
        else:
            ops.append(("op", token))
    return ops


if __name__ == "__main__":
    ensure_phase1_generated()
