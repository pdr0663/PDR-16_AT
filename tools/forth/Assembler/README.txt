Version 3.1
-----------

CODE has been implemented, and exists in two contexts.

On the host/compile side, in asm.py, use code(name, words, c=...) to define a precompiled Forth CODE word while building the image. The words list must contain only primitives from _primitives. Bare primitives are written as strings, and primitives with operands are written as (name, operand) tuples. Labels and branches are possible on the host side by using begin_code(), label(), code_primitive(), and end_code(). Example:

code('2DROP-CODE', ['DROP', 'DROP'])
code('LIT42', [('doLIT', 42), 'next'])

If you omit next, the assembler adds it automatically. For finer control, use begin_code(), code_primitive(), and end_code().

On the target/user side, inside eForth, CODE starts a new definition that compiles primitive opcodes directly, and END-CODE finishes it by appending _next, restoring interpret mode, and linking the word into the dictionary.

Inside a CODE ... END-CODE definition:
- Bare primitive names such as DROP, SWAP, OVER, UM+ are accepted directly.
- doLIT is also accepted, followed by one argument token.
- branch and ?branch are not supported on the user side.
- Immediate words still execute normally.

Example:

CODE 2DROP-CODE
  DROP
  DROP
END-CODE

Literal example:

CODE TRUE
  doLIT -1
END-CODE

The underscore-prefixed words such as _next, _DROP, and _doLIT are primitive opcode constants. They are available on the user side when you need the numeric opcode itself. END-CODE uses _next internally. In normal CODE bodies you usually write the bare primitive name, not the underscore form.

Use CODE words when the body is purely primitive-threaded. If you need normal Forth words, higher-level Forth calls, or structured compiling, use : instead.


