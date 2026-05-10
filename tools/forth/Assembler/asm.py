from __future__ import annotations

# An assembler for the PDR-16 computer, borrowed from the Gigatron project.
#
# SYNOPSIS: from asm import *
#
# *** From Gigatron... ***
# This is not an assembler -in- Python. This about using Python -itself- as an
# assembler! Specifically, asm.py is just the back end, while the Python
# interpreter acts as the front end. By using Python in this way, we get
# parsing and a powerful macro system for free. Assembly source files are
# Python files and not traditional .asm files. We recognize them with the
# .asm.py extension. During assembly we produce .lst files as a program
# listing in a more conventional notation.
#
# *** PDR-16 Assembler ***
# Heavily modified from the Gigatron assembler. Little if any remains from the
# original Gigatron code.

from dataclasses import dataclass
from inspect import currentframe
from os.path import basename, dirname, isabs, join, splitext
from types import FrameType
from typing import Literal
import importlib.util
import sys


def _load_primitive_metadata():
  module_path = join(dirname(dirname(__file__)), "Microcode Assembler", "primitive_metadata.py")
  spec = importlib.util.spec_from_file_location("pdr16_primitive_metadata", module_path)
  if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load primitive metadata from {module_path}")
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module._primitives


_primitives = _load_primitive_metadata()


# eForth configuration

# Version control

VER     = 0x04          # major release version
EXT     = 0x00          # minor extension

## Constants

COMPO   = 0x40         # lexicon compile only bit
IMEDD   = 0x80         # lexicon immediate bit
PRIMM   = 0x20         # lexicon primitive-shadow bit
PRIVV   = 0x0100       # vocabulary-private definition bit
LEX_LEN_MASK = 0x001F  # low 5 bits hold the counted-name length
LEX_ID_MASK = IMEDD | COMPO | PRIMM | PRIVV
LEX_LAST_CHAR_SHIFT = 9
LEX_LAST_CHAR_MASK = 0xFE00
LEX_NAME_MASK = LEX_LEN_MASK | LEX_LAST_CHAR_MASK
CELLL   = 1             # size of a cell
BASEE   = 10            # default radix
VOCSS   = 8             # depth of vocabulary stack

BKSPP   = 8             # backspace
LF      = 10            # line feed
CRR     = 13            # carriage return
ERR     = 27            # error escape
TIC     = 39            # tick

## Memory allocation  0//rom dict>------------------<sp//tib>--rp//em
# EM:
#         +-----------------------+
#         |                       |
# UPP     | USER VARIABLES        |
# RPP:    |                       | = EM - US
#         +-----------------------+
#         |                  |    |
#         | RETURN STACK     v    |
#         |                       |
#         +-----------------------+
#         |                       |
# SPP:    | TIB INPUT BUFFER   ^  |
# TIBB:   |                    |  |
#         +-----------------------+
#         |                  |    |
#         | DATA STACK       v    |
#         |                       |
#         +-----------------------+
#         |                       |
#         | USER DICTIONARY  ^    |
# CODER:  |                  |    | START OF RAM 32k
#         +-----------------------+
#         |                       |
#         | ROM DICTIONARY   ^    |
# CODEE:  |                  |    |
#         +-----------------------+
# USRV:   | USER VARS INIT        |
#         +-----------------------+
# COLDD:  | BOOT CODE             | START OF ROM
#         +-----------------------+

US      = 384 * CELLL   # user area reservation; must cover the full UZERO..ULAST template copy
RTS     = 128 * CELLL   # return stack size for the initial MEGA draft
TIBS    = 1024 * CELLL  # input buffer size
STS     = 128 * CELLL   # data stack size for the initial MEGA draft
EVALS   = 128 * CELLL   # transient per-line execution buffer size
FMTBS   = 512 * CELLL   # transient formatted-string buffer size

# V4 execution model encoding
PRIMITIVE_BITS = 6
PRIMITIVE_MAX = (1 << PRIMITIVE_BITS) - 1
# Keep execution tokens above the seeded user/bucket template footprint.
# The editor seed extends the user template beyond 0x0100, so keep the
# dictionary comfortably above it.
XT_BASE = 0x0200

# Memory map building from below
COLDD   = 0x0000        # cold start vector
USRV    = 0x0002        # *** WARNING CHECK THIS *** follows some boot code. Template user var area.
CODEE   = XT_BASE       # start of V4 execution-token dictionary space
CODER   = 0x8000        # start of the runtime user dictionary in RAM
CP_START = CODER        # runtime HERE after COLD; the build system grows ROM separately
# Memory map building down from top
EM      = 0x10000       # top of memory
UPP     = EM - US       # start of user area (UP)
RPP     = EM - US       # upper boundary of return stack / start of user area
TIBB    = RPP - TIBS    # terminal input buffer (TIB)
EVALB   = TIBB - EVALS  # transient per-line execution buffer
SPP     = EVALB - STS   # upper boundary of data stack
FMTB    = SPP - FMTBS   # transient formatted-string buffer
TOKEN_SCRATCH_START = FMTB - 0x0200 * CELLL  # scratch space for packed tokens, not a dictionary pointer
SP0_INIT = SPP - CELLL  # cached-stack idle SP: first usable spill slot
RP0_INIT = RPP - CELLL  # cached-stack idle RP: first usable spill slot below user vars


Value = int | str
CommentInput = None | str | list[str] | tuple[str, ...]
BodyValue = int | str | tuple[int | str, Value]


@dataclass(slots=True)
class Record:
  kind: Literal["org", "comment", "label", "emit"]
  addr: int | None = None
  size: int = 0
  text: str | None = None
  name: str | None = None
  mnemonic: str | None = None
  operand: Value | None = None
  data: int | str | list[Value] | None = None
  inline_comment: str | None = None


# Module variables because I don't feel like making a class
_currAddr = 0
_maxMemSize = 0x10000
_symbols: dict[str, int] = {}
_records: list[Record] = []
_LINK = 0               # most recent header address
_CURRENT_VOCABULARY = "FORTH"
_BUCKET_HEADS: dict[str, dict[str, int]] = {}
_USER = 4               # first user variable offset defined below
_definition_stack: list[dict[str, str]] = []
def _hexString(val: int) -> str:
  return f"${val & 0xFFFF:04x}"


def _normalize_comment_lines(comment: CommentInput) -> tuple[list[str], str | None]:
  if comment is None:
    return [], None
  if isinstance(comment, str):
    return [], comment

  lines = list(comment)
  if not lines:
    return [], None
  return lines[:-1], lines[-1]


def _append_comment_records(comment: CommentInput) -> str | None:
  lines, inline_comment = _normalize_comment_lines(comment)
  for line in lines:
    _records.append(Record(kind="comment", addr=_currAddr, text=line))
  return inline_comment


def _emit_record(record: Record) -> Record:
  global _currAddr
  record.addr = _currAddr
  _records.append(record)
  _currAddr += record.size
  if _currAddr > _maxMemSize:
    highlight(f"Error: assembly address {_hexString(_currAddr)} exceeds address space")
  return record


def _resolve_value(value: Value) -> int:
  if isinstance(value, int):
    return value
  if value in _primitives:
    return _primitives[value]["opcode"]
  if value in _symbols:
    return _symbols[value]
  highlight(f"Error: Undefined symbol {value!r}")
  return 0


def _resolve_primitive_opcode(value: int | str) -> int:
  if isinstance(value, int):
    return value
  if value in _primitives:
    return _primitives[value]["opcode"]
  raise Exception(f"Unknown primitive {value!r}.")


def _validate_u16(value: int, what: str) -> int:
  if not 0 <= value <= 0xFFFF:
    raise Exception(f"{what} must fit in 16 bits, got {value!r}.")
  return value


def _bucket_char(word: str) -> str | None:
  if not word:
    return None
  ch = word[0]
  if 32 <= ord(ch) <= 126:
    return ch
  return None


def _vocabulary_bucket_heads(vocabulary: str) -> dict[str, int]:
  bucket_heads = _BUCKET_HEADS.get(vocabulary)
  if bucket_heads is None:
    bucket_heads = {}
    _BUCKET_HEADS[vocabulary] = bucket_heads
  return bucket_heads


def seed_bucket_heads(vocabulary: str = "FORTH") -> list[int]:
  bucket_heads = _vocabulary_bucket_heads(vocabulary)
  return [bucket_heads.get(chr(code), 0) for code in range(32, 127)]


def set_current_vocabulary(vocabulary: str) -> None:
  global _CURRENT_VOCABULARY
  _CURRENT_VOCABULARY = vocabulary
  _vocabulary_bucket_heads(vocabulary)


def _encode_body_cell(value: BodyValue) -> Value:
  if isinstance(value, tuple):
    raise Exception(f"Bad V4 body cell {value!r}. Tuple body cells are no longer supported.")

  if isinstance(value, str):
    if value in _primitives:
      return _primitives[value]["opcode"]
    return value

  return value & 0xFFFF


def _start_word(
  word,
  c: CommentInput = None,
  immediate: bool | None = False,
  compile_only: bool | None = False,
  primitive_shadow: bool | None = False,
  private: bool | None = False,
  public: bool | None = True,
  vocabulary: str | None = None,
):
  global _LINK
  bucket_heads = _vocabulary_bucket_heads(vocabulary or _CURRENT_VOCABULARY)
  header_addr = pc()
  bucket_char = _bucket_char(word) if public else None
  bucket_link = bucket_heads.get(bucket_char, 0) if bucket_char is not None else 0
  if public:
    _LINK = header_addr
  header_comment = f"{word} {c}".strip() if c else word
  comment(header_comment)
  dw(bucket_link, c="bucket link")

  lex = len(word)
  if word:
    lex |= (ord(word[-1]) & 0x7F) << LEX_LAST_CHAR_SHIFT
  if immediate:
    lex |= IMEDD
  if compile_only:
    lex |= COMPO
  if primitive_shadow:
    lex |= PRIMM
  if private:
    lex |= PRIVV

  dw(lex, c=["", f"len('{word}')"])
  dw(word)
  label(word)
  if bucket_char is not None:
    bucket_heads[bucket_char] = header_addr


def _parse_code_op(op):
  if isinstance(op, str):
    return op, None
  if isinstance(op, tuple) and len(op) == 2:
    return op[0], op[1]
  raise Exception(f"Bad CODE operation {op!r}. Expected 'PRIM' or ('PRIM', operand).")


def _require_code_context():
  if not _definition_stack or _definition_stack[-1]["kind"] != "code":
    raise Exception("CODE primitive emission is only valid inside a CODE definition.")


def _emit_code_primitive(op, c=None):
  word, operand = _parse_code_op(op)
  if word not in _primitives:
    raise Exception(f"Bad CODE primitive {word!r}.")
  return p(word, operand=operand, c=c)


def _emit_opcode_only(word, c: CommentInput = None):
  if word not in _primitives:
    raise Exception(f"Bad primitive {word!r}.")
  return dw(_primitives[word]["opcode"], c=c)


def _format_values(values: list[int]) -> str:
  return " ".join(f"{value & 0xFFFF:04x}" for value in values)


def _render_data_words(data: int | str | list[Value]) -> list[int]:
  if isinstance(data, int):
    return [data]
  if isinstance(data, str):
    return [ord(letter) for letter in data]
  if isinstance(data, list):
    return [_resolve_value(word) for word in data]
  highlight(f"Error: Unsupported data type {type(data)!r}")
  return []


def _default_emit_comment(record: Record) -> str | None:
  if record.inline_comment:
    return record.inline_comment
  if isinstance(record.data, str):
    return repr(record.data)
  if isinstance(record.data, list):
    return " ".join(str(word) for word in record.data)
  return None


def _output_line(label: str = "", body: str = "", comment: str = "") -> str:
  label_field = f"{label}:" if label else ""
  comment_field = f"; {comment}" if comment else ""
  return f"{f'{label_field:<13}{body}':<60}{comment_field}\n"


def _write_record_listing(file, record: Record) -> None:
  if record.kind == "comment":
    if record.text == "":
      file.write("\n")
    else:
      file.write(_output_line(comment=record.text or ""))
    return

  if record.kind == "org":
    file.write(_output_line(body=f"org {_hexString(record.addr or 0)}"))
    return

  if record.kind == "label":
    file.write(_output_line(label=record.name or "", comment=record.inline_comment or ""))
    return

  if record.kind != "emit":
    return

  if record.mnemonic:
    opcode = _primitives[record.mnemonic]["opcode"]
    words = [opcode]
    if record.operand is not None:
      words.append(_resolve_value(record.operand))
  else:
    if record.data is None:
      return
    words = _render_data_words(record.data)

  addr = record.addr or 0
  body = f"{addr & 0xFFFF:04x}  {_format_values(words)}"
  file.write(_output_line(body=body, comment=_default_emit_comment(record) or ""))


def _record_words(record: Record) -> list[int]:
  if record.kind != "emit":
    return []

  if record.mnemonic:
    words = [_primitives[record.mnemonic]["opcode"]]
    if record.operand is not None:
      words.append(_resolve_value(record.operand))
    return words

  if record.data is None:
    return []
  return _render_data_words(record.data)


def _build_rom_image(max_words: int = CODER) -> bytearray:
  image = bytearray()
  current_addr = 0

  for record in _records:
    if record.kind == "org":
      current_addr = record.addr or 0
      if current_addr >= max_words:
        continue
      required_size = current_addr * 2
      if len(image) < required_size:
        image.extend(b"\x00" * (required_size - len(image)))
      continue

    if record.kind != "emit":
      continue

    addr = record.addr if record.addr is not None else current_addr
    if addr >= max_words:
      continue

    words = _record_words(record)
    if addr + len(words) > max_words:
      highlight(f"Error: ROM data at {_hexString(addr)} exceeds ROM limit {_hexString(max_words)}")

    offset = addr * 2
    payload = b"".join((word & 0xFFFF).to_bytes(2, "little") for word in words)
    end_offset = offset + len(payload)
    if len(image) < end_offset:
      image.extend(b"\x00" * (end_offset - len(image)))
    image[offset:end_offset] = payload

    current_addr = addr + len(words)

  required_size = max_words * 2
  if len(image) < required_size:
    image.extend(b"\x00" * (required_size - len(image)))
  elif len(image) > required_size:
    image = image[:required_size]

  return image


def link():
  return _LINK


def comment(text: str = ""):
  _records.append(Record(kind="comment", addr=_currAddr, text=text))


def org(addr, c: CommentInput = None):
  global _currAddr
  inline_comment = _append_comment_records(c)
  _currAddr = addr
  _records.append(Record(kind="org", addr=addr, inline_comment=inline_comment))


def define(name, newValue):
  if name in _symbols:
    oldValue = _symbols[name]
    if newValue != oldValue:
      highlight(f"Warning: redefining {name} (old {oldValue} new {newValue})")
  _symbols[name] = newValue


def addLabel(address, name, c: CommentInput = None):
  inline_comment = _append_comment_records(c)
  _records.append(Record(kind="label", addr=address, name=name, inline_comment=inline_comment))
  define(name, address)


def label(name, c: CommentInput = None):
  """Label the current address."""
  addLabel(_currAddr, name, c=c)


def p(word, operand=None, c: CommentInput = None):
  if word not in _primitives:
    highlight(f"Error: Bad word {word}")
    return None
  inline_comment = _append_comment_records(c)
  size = 1 + (1 if _primitives[word]["operands"] else 0)
  return _emit_record(
    Record(
      kind="emit",
      mnemonic=word,
      operand=operand,
      size=size,
      inline_comment=inline_comment,
    )
  )


def primitive_cell(word: int | str) -> int:
  """Encode a V4 primitive cell."""
  opcode = _resolve_primitive_opcode(word)
  if not 0 <= opcode <= PRIMITIVE_MAX:
    raise Exception(f"Primitive opcode must fit in {PRIMITIVE_BITS} bits, got {opcode}.")
  return opcode


def xt_cell(target: Value) -> int:
  """Encode a V4 execution token cell."""
  value = _validate_u16(_resolve_value(target), f"Execution token {target!r}")
  if value < XT_BASE:
    raise Exception(
      f"Execution token {target!r} resolved to {value:#06x}, below XT_BASE {XT_BASE:#06x}."
    )
  return value


def body(words: list[BodyValue], c: CommentInput = None):
  """Emit a V4 direct-execution word body."""
  return dw([_encode_body_cell(word) for word in words], c=c)


def dw(words, c: CommentInput = None):
  if isinstance(words, (list, str)):
    size = len(words)
  else:
    size = 1
  inline_comment = _append_comment_records(c)
  return _emit_record(
    Record(
      kind="emit",
      data=words,
      size=size,
      inline_comment=inline_comment,
    )
  )


def ds(word, string, c: CommentInput = None):
  """Insert a word token followed by a counted string in Forth format."""
  dw([word], c=c)
  dw(len(string))
  dw(string)


def begin_code(
  word,
  c: CommentInput = None,
  immediate: bool | None = False,
  compile_only: bool | None = False,
  public: bool | None = True,
):
  """Start a pre-compiled CODE word definition."""
  _start_word(word, c=c, immediate=immediate, compile_only=compile_only, public=public)
  _definition_stack.append({"kind": "code", "name": word})


def code_primitive(op, c: CommentInput = None):
  """Emit one primitive operation inside a CODE word."""
  _require_code_context()
  return _emit_code_primitive(op, c=c)


def code_opcode(word, c: CommentInput = None):
  """Emit only the opcode cell for a primitive inside a CODE word."""
  _require_code_context()
  return _emit_opcode_only(word, c=c)


def end_code(auto_next=True):
  """Finish a pre-compiled CODE word definition."""
  _require_code_context()
  context = _definition_stack.pop()
  if auto_next:
    p("EXIT", c=f"end CODE {context['name']}")


def colon(
  word,
  words,
  c: CommentInput = None,
  immediate: bool | None = None,
  compile_only: bool | None = None,
  public: bool | None = True,
):
  """Assemble a directly executable word body."""
  _start_word(word, c=c, immediate=immediate, compile_only=compile_only, public=public)
  body(words)
  # note, user must terminate the word with EXIT when appropriate


def code(
  word,
  words,
  c: CommentInput = None,
  immediate: bool | None = False,
  compile_only: bool | None = False,
  auto_next: bool = True,
  public: bool | None = True,
):
  """Macro to assemble a pre-compiled CODE word."""
  begin_code(word, c=c, immediate=immediate, compile_only=compile_only, public=public)
  for op in words:
    code_primitive(op)
  if auto_next and words:
    last_word, last_operand = _parse_code_op(words[-1])
    if last_word == "EXIT" and last_operand is None:
      auto_next = False
  end_code(auto_next=auto_next)


def primitive(word, c: CommentInput = None, public: bool | None = True):
  """Macro to assemble a primitive word."""
  stack = _primitives[word]["stack"]
  desc = f"{word} {stack}".strip()
  _start_word(word, c=f"{desc} {c}".strip() if c else desc, primitive_shadow=True, public=public)
  # Under V4, primitive words are ordinary directly executable words.
  # When reached via an execution token they should return through EXIT,
  # not via the old CODE-word-only `next` convention.
  _emit_opcode_only(word)
  _emit_opcode_only("EXIT")


def user(word, compile_only: bool | None = None, c: CommentInput = None, public: bool | None = True):
  """Macro to assemble a user variable word."""
  global _USER
  stub(word, compile_only=compile_only, c=c, public=public)
  body(["doLIT", _USER, "UP", "@", "+", "EXIT"])
  _USER += CELLL


def skip_user(cells: int = 1):
  """Advance the user-variable offset by a number of cells."""
  global _USER
  _USER += cells * CELLL


def variable(word, value, c=None, public: bool | None = True):
  """Macro to assemble a variable word."""
  _start_word(word, c=c, public=public)
  body(["doVAR"])
  dw(value, c=f"{word} data")


def constant(word, value=None, c=None, public: bool | None = True):
  """Macro to assemble a constant word."""
  if value is None:
    if word in _primitives:
      value = _primitives[word]["opcode"]
    else:
      highlight(f"Error: constant {word!r} requires an explicit value")
      return
  _start_word(word, c=c, public=public)
  body(["doLIT", value, "EXIT"])


def stub(
  word,
  immediate: bool | None = False,
  compile_only: bool | None = False,
  c: CommentInput = None,
  public: bool | None = True,
):
  """Macro to create a word header."""
  _start_word(word, c=c, immediate=immediate, compile_only=compile_only, public=public)
  # That's it. The word does nothing yet.


def symbol(name):
  """Lookup a symbol, return None if not defined."""
  return _symbols[name] if name in _symbols else None


def has(x):
  """Useful primitive."""
  return x is not None


def pc():
  """Current memory address."""
  return _currAddr


def writeRomFiles(sourceFile):
  stem, _ = splitext(sourceFile)
  stem, _ = splitext(stem)
  output_dir = dirname(stem)
  stem = basename(stem)
  if stem == "":
    stem = "out"
  if output_dir == "":
    output_dir = "."

  list_filename = join(output_dir, stem + ".lst")
  with open(list_filename, "w", encoding="utf-8") as file:
    for record in _records:
      _write_record_listing(file, record)

  image = _build_rom_image()
  lo_filename = join(output_dir, stem + "_lo.bin")
  with open(lo_filename, "wb") as file:
    file.write(image[0::2])

  hi_filename = join(output_dir, stem + "_hi.bin")
  with open(hi_filename, "wb") as file:
    file.write(image[1::2])

  print("Created file", list_filename)
  print("Created file", lo_filename)
  print("Created file", hi_filename)
  return list_filename


def _resolve_source_path(sourceFile: str) -> str:
  if isabs(sourceFile) or dirname(sourceFile):
    return sourceFile

  frame: FrameType | None = currentframe()
  caller: FrameType | None = frame.f_back if frame is not None else None
  try:
    while caller is not None:
      caller_file = caller.f_globals.get("__file__")
      if caller_file and caller_file != __file__:
        return join(dirname(caller_file), sourceFile)
      caller = caller.f_back
  finally:
    del caller
    del frame

  return sourceFile


def end(sourceFile="out"):
  """Resolve symbols and write output."""
  return writeRomFiles(_resolve_source_path(sourceFile))


# print() wrapper to highlight messages on terminal with ANSI escape codes
def highlight(*args):
  line = " ".join(str(arg) for arg in args)
  if sys.stdout.isatty():
    ansiBold = "\033[1m"
    ansiNormal = "\033[0m"
    print(ansiBold + line + ansiNormal)
  else:
    print(line)
  if line.upper().startswith("ERROR"):
    print("Assembly failed")
    sys.exit(1)
