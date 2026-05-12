from precompile_phase1 import ensure_phase1_generated

ensure_phase1_generated()

from generated_forth.precompiled_01_image import emit_precompiled_01_image
from generated_forth.precompiled_03_fstrings import emit_precompiled_03_fstrings
from generated_forth.precompiled_04_ansi import emit_precompiled_04_ansi
from generated_forth.precompiled_07_math import emit_precompiled_07_math
from generated_forth.precompiled_08_editor import emit_precompiled_08_editor

from asm import (
    BASEE,
    BKSPP,
    CELLL,
    CODEE,
    CODER,
    COLDD,
    COMPO,
    CP_START,
    CRR,
    EVALB,
    EM,
    ERR,
    EXT,
    FMTB,
    FMTBS,
    LF,
    IMEDD,
    LEX_LEN_MASK,
    LEX_NAME_MASK,
    PRIVV,
    PRIMM,
    RP0_INIT,
    RPP,
    RTS,
    SP0_INIT,
    SPP,
    STS,
    TOKEN_SCRATCH_START,
    TIBS,
    TIBB,
    XT_BASE,
    UPP,
    USRV,
    VER,
    VOCSS,
    _primitives,
    begin_code,
    body,
    code,
    code_opcode,
    code_primitive,
    colon,
    comment,
    constant,
    define,
    ds,
    dw,
    end,
    end_code,
    label,
    link,
    org,
    p,
    pc,
    primitive,
    seed_bucket_heads,
    skip_user,
    symbol,
    stub,
    user,
    variable,
)


def ordered_primitives(attribute: str) -> list[str]:
    return sorted(
        (word for word, meta in _primitives.items() if meta.get(attribute)),
        key=lambda word: _primitives[word]["opcode"],
    )

####################
# Bottom of memory #
####################

org(COLDD)

p('jump', "COLD")


################################
# User variable initialization #
################################

org(USRV)
label('UZERO')
UZERO = pc()

for i in range(4):
    dw(0, c='Reserved')   # reserved
dw(SP0_INIT, c='SP0 = SPP-1')     # SP0
dw(RP0_INIT, c='RP0 = RPP-1')     # RP0
dw(['?rx'], c='?KEY = ?rx')   # '?KEY
dw(['tx!'], c='EMIT = tx!')   # 'EMIT
dw(['accept'], c='EXPECT = accept')# 'EXPECT
dw(['kTAP'], c='TAP = kTAP')  # 'TAP
dw(['tx!'], c="'ECHO = tx!")  	# 'ECHO
dw(['.OK'], c='PROMPT = .OK')	  # 'PROMPT
dw(['hi'], c='BOOT = hi')      # 'BOOT
dw(['FIND-RUNTIME'], c='FIND = FIND-RUNTIME')   # 'FIND
dw(BASEE, c='BASE = 10')	# BASE
dw(BASEE, c='BASEHOLD = 10')	# BASEHOLD
dw(0, c='tmp')   	  # tmp
dw(0, c='STRX')   	  # STRX
dw(0, c='%mta')   	  # %mta
dw(0, c='%mtu')   	  # %mtu
dw(0, c='%mtw')   	  # %mtw
dw(0, c='%mtp')   	  # %mtp
dw(0, c='%mtf')   	  # %mtf
dw(0, c='%mtl')   	  # %mtl
dw(0, c='SPAN')   	  # SPAN
label('UZERO_TO_IN')
dw(0, c='>IN')   	  # >IN
label('UZERO_NUM_TIB')
dw(0, c='#TIB')   	  # #TIB
label('UZERO_TIB')
dw(TIBB, c='TIB')    # TIB
dw(0, c='CSP')   	  # CSP
dw(0, c='STATE')   	  # STATE
dw(0, c='HLD')   	  # HLD
dw(0, c='HANDLER')   	  # HANDLER
label('UZERO_EKEY_HEAD')
dw(0, c='EKEY head')
label('UZERO_EKEY_TAIL')
dw(0, c='EKEY tail')
label('UZERO_EKEY_BUFFER')
for _ in range(16):
    dw(0, c='EKEY buffer')
label('UZERO_FORTHVOC')
dw(0, c='FORTHVOC bucket table ptr')
dw(0, c='FORTHVOC next vocabulary')
dw(0, c='FORTHVOC metadata')
label('UZERO_CONTEXT')
dw(0, c='CONTEXT')   	  # CONTEXT pointer
for i in range(VOCSS):
    dw(0, c='VOCAB')	  # vocabulary stack
label('UZERO_CURRENT')
dw(0, c='CURRENT')   	  # CURRENT pointer
dw(0, c='CURRENT bucket table') # stable current vocabulary record
label('UZERO_CP')
dw(CP_START, c='CP = runtime HERE')   # CP
dw(TOKEN_SCRATCH_START, c='TOKBUF token scratch')   # token scratch buffer in high RAM
dw(EVALB, c='LP')   # transient per-line execution buffer pointer
label('UZERO_LAST')
dw(['LASTN'])	# LAST
dw(0, c='find token scratch')
dw(0, c='find first-char scratch')
dw(0, c='find lex scratch')
dw(0, c='find private-visible scratch')
dw(0, c='find stats enabled scratch')
dw(0, c='find visits scratch')
dw(0, c='find full-compare scratch')
dw(0, c='find hit-depth scratch')
dw(0, c='image cell-count scratch')
dw(0, c='image width scratch')
dw(0, c='find bucket scratch')
dw(0, c='bucket head scratch')
label('UZERO_MODULE_ACTIVE')
dw(0, c='module active flag')
label('UZERO_MODULE_FAILED')
dw(0, c='module failed flag')
label('UZERO_MODULE_LAST')
dw(0, c='module saved LAST')
label('UZERO_MODULE_CP')
dw(0, c='module saved CP')
label('UZERO_MODULE_FORTHVOC')
dw(0, c='module saved FORTHVOC bucket table ptr')
dw(0, c='module saved FORTHVOC next vocabulary')
dw(0, c='module saved FORTHVOC metadata')
label('UZERO_MODULE_CONTEXT')
dw(0, c='module saved CONTEXT')
for _ in range(VOCSS):
    dw(0, c='module saved VOCAB')
label('UZERO_MODULE_CURRENT')
dw(0, c='module saved CURRENT')
dw(0, c='module saved VOCAB LINK')
FORTH_BUCKET_HEADS_OFFSET = pc() - symbol('UZERO')
label('FORTH_BUCKET_HEADS_TEMPLATE')
for _ in range(95):
    dw(0, c='FORTH bucket template')
# Reserve the editor USER slots in the copied UZERO template so the seeded
# editor words can bind to stable, initialized user-area cells.
EDITOR_USER_OFFSET = 256
EDITOR_USER_CELLS = 26
while (pc() - symbol('UZERO')) < EDITOR_USER_OFFSET:
    dw(0, c='editor user pad')
for _ in range(EDITOR_USER_CELLS):
    dw(0, c='editor user slot')
label('ULAST')
ULAST = pc()
FORTH_BUCKET_HEADS_RAM = UPP + FORTH_BUCKET_HEADS_OFFSET

###########################
# Forth Dictionary begins #
###########################

org(CODEE)

#
#;; System and user variables
#

# Step over first 4 cells. Reserved.
_USER = 4 * CELLL

#;   SP0		( -- a )
#;		Pointer to bottom of the data stack.
user('SP0')

#   RP0		( -- a )
#		Pointer to bottom of the return stack.
user('RP0')

#   '?KEY	( -- a )
#		Execution vector of ?KEY.
user("'?KEY")

#   'EMIT	( -- a )
#		Execution vector of EMIT.
user("'EMIT")

#   'EXPECT	( -- a )
#		Execution vector of EXPECT.
user("'EXPECT")

#   'TAP	( -- a )
#		Execution vector of TAP.
user("'TAP")

#   'ECHO	( -- a )
#		Execution vector of ECHO.
user("'ECHO")

#   'PROMPT	( -- a )
#		Execution vector of PROMPT.
user("'PROMPT")

#   'BOOT	( -- a )
#		Execution vector of BOOT.
user("'BOOT")

#   'FIND	( -- a )
#		Execution vector of FIND.
user("'FIND")

#   BASE	( -- a )
#		Storage of the radix base for numeric I/O.
user('BASE')

#   BASEHOLD	( -- a )
#		Saved radix base for source-managed base changes.
user('BASEHOLD')

#   tmp		( -- a )
#		A temporary storage location used in parse and find.
user('tmp', compile_only = True)

#   STRX	( -- a )
#		A temporary string-target storage location.
user('STRX')

#   %mta	( -- a )
#		Current f-string parse address.
user('%mta')

#   %mtu	( -- a )
#		Remaining f-string length.
user('%mtu')

#   %mtw	( -- a )
#		Current f-string field width.
user('%mtw')

#   %mtp	( -- a )
#		Current f-string precision (-1 when absent).
user('%mtp')

#   %mtf	( -- a )
#		Current f-string parse flag.
user('%mtf')

#   %mtl	( -- a )
#		Current transient formatted-string length.
user('%mtl')

#   SPAN	( -- a )
#		Hold character count received by EXPECT.
user('SPAN')

#   >IN		( -- a )
#		Hold the character pointer while parsing input stream.
user('>IN')

#   #TIB	( -- a )
#		Hold the current count and address of the terminal input buffer.
user('#TIB')
skip_user()

#   CSP		( -- a )
#		Hold the stack pointer for error checking.
user('CSP')

#   STATE	( -- a )
#		Interpreter state. 0=interpret, non-zero=compile.
user('STATE')

#   HLD		( -- a )
#		Hold a pointer in building a numeric output string.
user('HLD')

#   HANDLER	( -- a )
#		Hold the return stack pointer for error handling.
user('HANDLER')

#   EKEY-HEAD	( -- a )
#		Ring-buffer write index for normalized key events.
user('EKEY-HEAD', public=False)

#   EKEY-TAIL	( -- a )
#		Ring-buffer read index for normalized key events.
user('EKEY-TAIL', public=False)
skip_user(16)

#   FORTHVOC	( -- a )
#		Writable FORTH vocabulary record.
user('FORTHVOC')
skip_user(2)

#   CONTEXT	( -- a )
#		A area to specify vocabulary search order.
user('CONTEXT')
skip_user(VOCSS)	# vocabulary stack

#   CURRENT	( -- a )
#		Point to the vocabulary to be extended.
user('CURRENT')
skip_user()		# vocabulary link pointer

#   CP		( -- a )
#		Runtime dictionary allocation pointer (HERE).
user('CP')

#   TOKBUF	( -- a )
#		Point to the token scratch buffer.
user('TOKBUF')

#   LP		( -- a )
#		Point to the transient per-line execution buffer.
user('LP')

#   LAST	( -- a )
#		Point to the last dictionary header.
user('LAST')
user('FIND_TOKEN')
user('FIND_CHAR')
user('FIND_LEX')
user('FIND_PRIVATE')
user('FIND_STATS')
user('FIND_VISITS')
user('FIND_FULLS')
user('FIND_HIT')
user('IMG-CELLS')
user('IMGW')
user('FIND_BUCKET')
user('BUCKET_HEAD')


# Words to support system and user variables
# colon('doVAR', ['R>', 'EXIT'], compile_only=True, c='( -- a)')
variable('UP', UPP, c='( -- a, Pointer to the user area.)')
colon('doUSER', ['R>', '@', 'UP', '@', '+', 'EXIT'], compile_only=True, public=False, c='( -- a )')
colon('MODULE_ACTIVE', ['doLIT', symbol('UZERO_MODULE_ACTIVE') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_FAILED', ['doLIT', symbol('UZERO_MODULE_FAILED') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_LAST', ['doLIT', symbol('UZERO_MODULE_LAST') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_CP', ['doLIT', symbol('UZERO_MODULE_CP') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_FORTHVOC', ['doLIT', symbol('UZERO_MODULE_FORTHVOC') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_CONTEXT', ['doLIT', symbol('UZERO_MODULE_CONTEXT') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')
colon('MODULE_CURRENT', ['doLIT', symbol('UZERO_MODULE_CURRENT') - symbol('UZERO'), 'UP', '@', '+', 'EXIT'], public=False, c='( -- a )')


# Words to support Forth vocabulary
colon('doVOC', [], compile_only=True, public=False, c='( -- )')
dw(['R>', '@', 'VOCAB>BUCKETS', 'CONTEXT', 'CELL+', '!'])
dw(['FORTHVOC', 'CONTEXT', 'CELL+', 'CELL+', '!'])
dw(['doLIT', 0, 'CONTEXT', 'CELL+', 'CELL+', 'CELL+', '!'])
dw(['CONTEXT', 'CELL+', 'CONTEXT', '!', 'EXIT'])
colon('FORTH', ['FORTHVOC', 'DUP', 'CONTEXT', '!', 'DROP', 'EXIT'], c='( -- )')

# Common functions
colon('?DUP', [], c="( w -- w w | 0 )")
dw(['DUP', '?branch', 'QDUP1'])
dw(['DUP', 'EXIT'])
label('QDUP1')
dw(['EXIT'])

colon("ROT", ['>R', 'SWAP', 'R>', 'SWAP', 'EXIT'], c='( w1 w2 w3 -- w2 w3 w1 )')
colon("2DROP", ['DROP', 'DROP', 'EXIT'], c='( w w  -- )')
colon('DNEGATE', ['doLIT', -1, 'XOR', '>R', 'doLIT', -1, 'XOR', 'doLIT', 1, 'UM+', 'R>', 'UM+', 'DROP', 'EXIT'], c='( d -- -d )')
colon('D+', ['>R', 'SWAP', '>R', 'UM+', 'R>', 'R>', 'UM+', 'DROP', 'UM+', 'DROP', 'EXIT'], c='( d d -- d )')

# Comparison

begin_code('U<', c='( u u -- t )')
body(['OVER', 'OVER', 'XOR', '0<', '?branch'])
dw(['ULES1'])
body(['SWAP', 'DROP', '0<', 'EXIT'])
label('ULES1')
body(['-', '0<', 'EXIT'])
end_code(auto_next=False)

colon('<',         [], c='( n n -- t )') 
dw(['2DUP', 'XOR', '0<'])
dw(['?branch', 'LESS1'])
dw(['DROP', '0<', 'EXIT'])
label('LESS1')
dw(['-', '0<', 'EXIT'])

colon('MAX',       [], c='( n n -- n )')
dw(['2DUP', '<'])
dw(['?branch', 'MAX1'])
dw(['SWAP'])
label('MAX1')
dw(['DROP', 'EXIT'])

colon('MIN',       [], c='( n n -- n )') 
dw(['2DUP', 'SWAP', '<'])
dw(['?branch', 'MIN1'])
dw(['SWAP'])
label('MIN1')
dw(['DROP', 'EXIT'])

colon('WITHIN',    ['OVER', '-', '>R', '-', 'R>', 'U<', 'EXIT'], c='( u ul uh -- t )')

# Divide
begin_code('UM/MOD', c='( ud u -- ur uq )')
body(['2DUP', 'U<', '?branch'])
dw(['UMM4'])
body(['NEGATE', 'doLIT'])
dw(-16)
body(['>R'])
label('UMM1')
body(['>R', 'DUP', 'UM+', '>R', '>R', 'DUP', 'UM+', 'R>', '+', 'DUP', 'R>', 'R@', 'SWAP', '>R', 'UM+', 'R>', 'OR', '?branch'])
dw(['UMM2'])
body(['>R', 'DROP', 'doLIT'])
dw(1)
body(['+', 'R>', 'branch'])
dw(['UMM3'])
label('UMM2')
body(['DROP'])
label('UMM3')
body(['R>', 'doNEXT', 'UMM1', 'R>', 'DROP', 'DROP', 'SWAP', 'EXIT'])
label('UMM4')
body(['DROP', '2DROP', 'doLIT'])
dw(-1)
body(['DUP', 'EXIT'])
end_code(auto_next=False)

colon('M/MOD', [], c='( d n -- r q ) floored division')
dw(['DUP', '0<', 'DUP', '>R'])
dw(['?branch', 'MMOD1'])
dw(['NEGATE', '>R', 'DNEGATE', 'R>'])
label('MMOD1')
dw(['>R', 'DUP', '0<'])
dw(['?branch', 'MMOD2'])
dw(['R@', '+'])
label('MMOD2')
dw(['R>', 'UM/MOD', 'R>'])
dw(['?branch', 'MMOD3'])
dw(['SWAP', 'NEGATE', 'SWAP'])
label('MMOD3')
dw(['EXIT'])

colon('/MOD', ["OVER", "0<", "SWAP", "M/MOD", 'EXIT'], c='( n n -- r q )')
colon('MOD', ["/MOD", "DROP", 'EXIT'], c='( n n -- r )')
# Multiply
primitive('UM*', c='( u u -- ud )')

colon('*', ['UM*', 'DROP', 'EXIT'], c='( n n -- n )')

colon('M*', [], c='( n n -- d )')
dw(['2DUP', 'XOR', '0<', '>R'])
dw(['ABS', 'SWAP', 'ABS', 'UM*'])
dw(['R>'])
dw(['?branch', 'MSTA1'])
dw(['DNEGATE'])
label('MSTA1')
dw(['EXIT'])  

colon('*/MOD', ['>R', 'M*', 'R>', 'M/MOD', 'EXIT'], c='( n n n -- r q )')
colon('*/', ['*/MOD', 'SWAP', 'DROP', 'EXIT'], c='( n n n -- q )')

# Memory alignment
colon('CELL-', ['doLIT', -1, 'UM+', 'DROP', 'EXIT'], c='(a -- a)')
colon('CELL+', ['doLIT', 1, 'UM+', 'DROP', 'EXIT'], c='(a -- a)')
code('CELLS', [], c='(n -- n)')

colon('ALIGNED', [], c='(b -- a)')
dw (['EXIT']) # alignment is redundant on PDR-16

colon('BL', ['doLIT', 32, 'EXIT'], c='(-- 32)')

colon('>CHAR', [], c='(c -- c)')
dw(['doLIT', 0x7F, 'AND', 'DUP'])
dw(['doLIT', 127, 'BL', 'WITHIN'])
dw(['?branch', 'TCHA1'])
dw(['DROP', 'doLIT', 95]) # ASCII 95 = '_'
label('TCHA1')
dw(['EXIT'])

colon('DEPTH', ['SP0', '@', 'SP@', '-', 'doLIT', 1, '-', 'EXIT'], c='(-- n)')

colon('PICK', ['doLIT', 1, '+', 'CELLS', 'SP@', '+', '@', 'EXIT'], c='(+n -- w)')

# Memory access
code('+!', ['SWAP', 'OVER', '@', 'UM+', 'DROP', 'SWAP', '!'], c='(n a --)')

colon('2!', ['SWAP', 'OVER', '!', 'doLIT', 1, 'UM+', 'DROP', '!', 'EXIT'], c='(d a --)')
colon('2@', ['DUP', 'doLIT', 1, 'UM+', 'DROP', '@', 'SWAP', '@', 'EXIT'], c='(a -- d)')

colon('COUNT', ['DUP', 'doLIT', 1, 'UM+', 'DROP', 'SWAP', 'C@', 'EXIT'], c='(b -- b +n)')

colon('HERE', ['CP', '@', 'EXIT'], c='(-- a)')
colon('PAD', ['HERE', 'doLIT', 80, '+', 'EXIT'], c='(-- a)')
colon('TIB', ['#TIB', 'CELL+', '@', 'EXIT'], c='(-- a)')
colon('LINEBUF', ['doLIT', EVALB, 'EXIT'], public=False, c='(-- a)')
colon('LINE-RESET', ['doLIT', EVALB, 'LP', '!', 'EXIT'], compile_only=True, public=False, c='(--)')
colon('LINE,', ['LP', '@', 'DUP', 'CELL+', 'LP', '!', '!', 'EXIT'], compile_only=True, public=False, c='( w -- )')
colon('LINE-LIT', ['doLIT', _primitives['doLIT']['opcode'], 'LINE,', 'LINE,', 'EXIT'], compile_only=True, public=False, c='( n -- )')
colon('LINE-RUN', ['doLIT', _primitives['EXIT']['opcode'], 'LINE,', 'doLIT', EVALB, '>R', 'EXIT'], compile_only=True, public=False, c='(--)')
colon('RUN-XT', ['LINE-RESET', 'LINE,', 'LINE-RUN'], compile_only=True, public=False, c='( xt -- )')
colon('LINE-END', ['doLIT', '.OK', 'LINE,', 'doLIT', _primitives['EXIT']['opcode'], 'LINE,', 'doLIT', EVALB, '>R', 'EXIT'], compile_only=True, public=False, c='(--)')

colon('CMOVE', [], c='(b b u --)')
dw(['branch', 'CMOV2'])
label('CMOV1')
dw(['>R', 'OVER', 'C@', 'OVER', 'C!'])
dw(['doLIT', 1, '+', 'SWAP', 'doLIT', 1, '+', 'SWAP'])
dw(['R>', 'doLIT', -1, '+'])
label('CMOV2')
dw(['DUP', '?branch', 'CMOV3'])
dw(['branch', 'CMOV1'])
label('CMOV3')
dw(['DROP', '2DROP', 'EXIT'])

colon('FILL', [], c='(b u c --)')
dw(['SWAP', 'NEGATE', '>R', 'SWAP'])
dw(['branch', 'FILL2'])
label('FILL1')
dw(['2DUP', 'C!', 'doLIT', 1, '+'])
label('FILL2')
dw(['doNEXT', 'FILL1', 'R>', 'DROP'])
dw(['2DROP', 'EXIT'])

colon('-TRAILING', [], c='(b u -- b u)')
dw(['NEGATE', '>R'])
dw(['branch', 'DTRA2'])
label('DTRA1')
dw(['BL', 'OVER', 'R@', '+', 'C@', '<'])
dw(['?branch', 'DTRA2'])
dw(['R>', 'doLIT', 1, '+', 'EXIT'])
label('DTRA2')
dw(['doNEXT', 'DTRA1', 'R>', 'DROP'])
dw(['doLIT', 0, 'EXIT'])

colon('PACK$', [], c='(b u a -- a)')
dw(['ALIGNED', 'DUP', '>R', 'OVER'])
dw(['DUP', 'doLIT', 0, 'doLIT', 1, 'UM/MOD', 'DROP'])
dw(['-', 'OVER', '+', 'doLIT', 0, 'SWAP', '!', '2DUP', 'C!', 'doLIT', 1, '+', 'SWAP', 'CMOVE', 'R>', 'EXIT'])

# Numeric output
colon('DIGIT', ['doLIT', 9, 'OVER', '<', 'doLIT', 7, 'AND', '+', 'doLIT', 48, '+', 'EXIT'], c='(u -- c)')
colon('EXTRACT', ['doLIT', 0, 'SWAP', 'UM/MOD', 'SWAP', 'DIGIT', 'EXIT'], c='(n base -- n c)')

colon('<#', ['PAD', 'HLD', '!', 'EXIT'], c='(--)')

colon('HOLD', ['HLD', '@', 'doLIT', 1, '-', 'DUP', 'HLD', '!', 'C!', 'EXIT'], c='(c --)')

colon('#', ['BASE', '@', 'EXTRACT', 'HOLD', 'EXIT'], c='(u -- u)')

colon('#S', [], c='(u -- 0)')
label('DIGS1')
dw(['#', 'DUP'])
dw(['?branch', 'DIGS2'])
dw(['branch', 'DIGS1'])
label('DIGS2')
dw(['EXIT'])

colon('SIGN', [], c='(n --)')
dw(['0<'])
dw(['?branch', 'SIGN1'])
dw(['doLIT', 45, 'HOLD']) # ASCII 45 = '-'
label('SIGN1')
dw(['EXIT'])

colon('#>', ['DROP', 'HLD', '@', 'PAD', 'OVER', '-', 'EXIT'], c='(w -- b u)')

# Number output
colon('str', [], c='(n -- b u)')
dw(['DUP', '>R', 'ABS', '<#', '#S', 'R>', 'SIGN', '#>', 'EXIT'])

colon('HEX', ['doLIT', 16, 'BASE', '!', 'EXIT'], c='(--)')

colon('DECIMAL', ['doLIT', 10, 'BASE', '!', 'EXIT'], c='(--)')

colon('>BASE', ['BASE', '@', 'BASEHOLD', '!', 'EXIT'], c='( -- )')

colon('BASE>', ['BASEHOLD', '@', 'BASE', '!', 'EXIT'], c='( -- )')

colon('.R', [], c='(n +n --)')
dw(['>R', 'str'])
dw(['R>', 'OVER', '-', 'SPACES'])
dw(['TYPE', 'EXIT'])

colon('U.R', [], c='(u +n --)')
dw(['>R'])
dw(['<#', '#S', '#>', 'R>'])
dw(['OVER', '-', 'SPACES'])
dw(['TYPE', 'EXIT'])

colon('U.', [], c='(u --)')
dw(['<#', '#S', '#>'])
dw(['SPACE'])
dw(['TYPE', 'EXIT'])

colon('.', [], c='(w --)')
dw(['BASE', '@', 'doLIT', 10, 'XOR'])
dw(['?branch', 'DOT1'])
dw(['U.', 'EXIT'])
label('DOT1')
dw(['str', 'SPACE', 'TYPE', 'EXIT'])

colon('?', [], c='(a --)')
dw(['@', '.', 'EXIT'])

# Numeric output
colon('DIGIT?', [], c='(c base -- u t)')
dw(['>R', 'doLIT', ord('0'), '-', 'doLIT', 9, 'OVER', '<'])
dw(['?branch', 'DGTQ1'])
dw(['doLIT', 7, '-', 'DUP', 'doLIT', 10, '<', 'OR'])
label('DGTQ1')
dw(['DUP', 'R>', 'U<', 'EXIT'])

colon('NUMBER?', [], c='(a -- n T | a F)')
dw(['BASE', '@', '>R', 'DUP', 'COUNT'])
dw(['OVER', 'C@', 'doLIT', ord('$'), '=']) # ASCII 36 = '$'
dw(['?branch', 'NUMQ1'])
dw(['HEX', 'SWAP', 'doLIT', 1, '+'])
dw(['SWAP', 'doLIT', 1, '-'])
label('NUMQ1')
dw(['OVER', 'C@', 'doLIT', ord('-'), '='])
dw(['DUP', 'tmp', '!'])
dw(['?branch', 'NUMQ2'])
dw(['SWAP', 'doLIT', 1, '+'])
dw(['SWAP', 'doLIT', 1, '-'])
label('NUMQ2')
dw(['DUP'])
dw(['?branch', 'NUMQ6'])
dw(['BASE', '@', 'doLIT', 16, 'XOR'])
dw(['?branch', 'NUMQ16'])
dw(['BASE', '@', 'doLIT', 10, 'XOR'])
dw(['?branch', 'NUMQ10'])
dw(['NEGATE', '>R'])
dw(['doLIT', 0])
label('NUMQ3')
dw(['OVER', 'C@', 'BASE', '@', 'DIGIT?'])
dw(['?branch', 'NUMQ4'])
dw(['SWAP', 'BASE', '@', '*', '+'])
dw(['SWAP', 'doLIT', 1, '+', 'SWAP'])
dw(['doNEXT', 'NUMQ3', 'R>', 'DROP'])
dw(['branch', 'NUMQ5A'])
label('NUMQ16')
dw(['NEGATE', '>R'])
dw(['doLIT', 0])
label('NUMQ17')
dw(['OVER', 'C@', 'HEX?'])
dw(['?branch', 'NUMQ4'])
dw(['SWAP', '<<4', '+'])
dw(['SWAP', 'doLIT', 1, '+', 'SWAP'])
dw(['doNEXT', 'NUMQ17', 'R>', 'DROP'])
dw(['branch', 'NUMQ5A'])
label('NUMQ10')
dw(['NEGATE', '>R'])
dw(['doLIT', 0])
label('NUMQ11')
dw(['OVER', 'C@', 'DUP', 'DIGIT-CHAR?'])
dw(['?branch', 'NUMQ4D'])
dw(['doLIT', ord('0'), '-'])
dw(['SWAP', 'doLIT', 10, '*', '+'])
dw(['SWAP', 'doLIT', 1, '+', 'SWAP'])
dw(['doNEXT', 'NUMQ11', 'R>', 'DROP'])
label('NUMQ5A')
dw(['SWAP', 'DROP', 'SWAP', 'DROP'])
dw(['tmp', '@'])
dw(['?branch', 'NUMQ5'])
dw(['NEGATE'])
label('NUMQ5')
dw(['doLIT', -1, 'R>', 'BASE', '!', 'EXIT'])
label('NUMQ4')
dw(['DROP', 'R>', 'DROP', '2DROP'])
dw(['doLIT', 0, 'R>', 'BASE', '!', 'EXIT'])
label('NUMQ4D')
dw(['DROP'])
dw(['R>', 'DROP', '2DROP'])
dw(['doLIT', 0, 'R>', 'BASE', '!', 'EXIT'])
label('NUMQ6')
dw(['DROP', 'DROP'])
dw(['doLIT', 0, 'R>', 'BASE', '!', 'EXIT'])

# Basic I/O
colon('?KEY', ['?rx', 'EXIT'], c='(-- c T | F)')

colon('KEY', [], c='(-- c)')
label('KEY1')
dw(['?KEY'])
dw(['?branch', 'KEY1'])
dw(['EXIT'])

colon('EKEY-BUF', ['doLIT', symbol('UZERO_EKEY_BUFFER') - symbol('UZERO'), '+', 'UP', '@', '+', 'EXIT'], public=False, c='( i -- a )')

colon('?EKEY', [], c='(-- key T | F)')
dw(['EKEY-HEAD', '@', 'EKEY-TAIL', '@', '='])
dw(['?branch', 'QEKEY1'])
dw(['doLIT', 0, 'EXIT'])
label('QEKEY1')
dw(['EKEY-TAIL', '@', 'DUP', 'EKEY-BUF', '@'])
dw(['SWAP', 'doLIT', 1, '+', 'doLIT', 0x000F, 'AND', 'EKEY-TAIL', '!'])
dw(['doLIT', -1, 'EXIT'])

colon('EKEY', [], c='(-- key)')
label('EKEY1')
dw(['?EKEY'])
dw(['?branch', 'EKEY1'])
dw(['EXIT'])

colon('KEY_UP', ['doLIT', 0x01, 'EXIT'], c='(-- keycode)')
colon('KEY_DOWN', ['doLIT', 0x02, 'EXIT'], c='(-- keycode)')
colon('KEY_LEFT', ['doLIT', 0x03, 'EXIT'], c='(-- keycode)')
colon('KEY_RIGHT', ['doLIT', 0x04, 'EXIT'], c='(-- keycode)')
colon('KEY_HOME', ['doLIT', 0x05, 'EXIT'], c='(-- keycode)')
colon('KEY_END', ['doLIT', 0x06, 'EXIT'], c='(-- keycode)')
colon('KEY_PGUP', ['doLIT', 0x07, 'EXIT'], c='(-- keycode)')
colon('KEY_PGDN', ['doLIT', 0x08, 'EXIT'], c='(-- keycode)')
colon('KEY_INS', ['doLIT', 0x09, 'EXIT'], c='(-- keycode)')
colon('KEY_DEL', ['doLIT', 0x0A, 'EXIT'], c='(-- keycode)')
colon('KEY_BACKSPACE', ['doLIT', 0x0B, 'EXIT'], c='(-- keycode)')
colon('KEY_ENTER', ['doLIT', 0x0C, 'EXIT'], c='(-- keycode)')
colon('KEY_F1', ['doLIT', 0x11, 'EXIT'], c='(-- keycode)')
colon('KEY_F2', ['doLIT', 0x12, 'EXIT'], c='(-- keycode)')
colon('KEY_F3', ['doLIT', 0x13, 'EXIT'], c='(-- keycode)')
colon('KEY_F4', ['doLIT', 0x14, 'EXIT'], c='(-- keycode)')
colon('KEY_F5', ['doLIT', 0x15, 'EXIT'], c='(-- keycode)')
colon('KEY_F6', ['doLIT', 0x16, 'EXIT'], c='(-- keycode)')
colon('KEY_F7', ['doLIT', 0x17, 'EXIT'], c='(-- keycode)')
colon('KEY_F8', ['doLIT', 0x18, 'EXIT'], c='(-- keycode)')
colon('KEY_F9', ['doLIT', 0x19, 'EXIT'], c='(-- keycode)')
colon('KEY_F10', ['doLIT', 0x1A, 'EXIT'], c='(-- keycode)')

colon('EMIT', ['tx!', 'EXIT'], c='(c --)')

colon('NUF?', [], c='(-- f)')
dw(['?KEY', 'DUP'])
dw(['?branch', 'NUFQ1'])
dw(['2DROP', 'KEY', 'doLIT', CRR, '='])
label('NUFQ1')
dw(['EXIT'])

colon('PACE', ['doLIT', 11, 'EMIT', 'EXIT'], c='(--)')
colon('SPACE', ['BL', 'EMIT', 'EXIT'], c='(--)')

colon('CHARS', [], c='(+n c --)')
dw(['SWAP', 'doLIT', 0, 'MAX', 'doLIT', 1, '+', 'NEGATE', '>R'])
dw(['branch', 'CHARS2'])
label('CHARS1')
dw(['DUP', 'EMIT'])
label('CHARS2')
dw(['doNEXT', 'CHARS1', 'R>', 'DROP'])
dw(['DROP', 'EXIT'])

colon('SPACES', ['BL', 'CHARS', 'EXIT'], c='(+n --)')

colon('TYPE', [], c='(b u --)')
dw(['branch', 'TYPE2'])
label('TYPE1')
dw(['SWAP', 'DUP', 'C@', 'EMIT'])
dw(['doLIT', 1, '+', 'SWAP', 'doLIT', -1, '+'])
label('TYPE2')
dw(['DUP', '?branch', 'TYPE3'])
dw(['branch', 'TYPE1'])
label('TYPE3')
dw(['2DROP', 'EXIT'])

colon('CR', ['doLIT', 13, 'EMIT', 'doLIT', 10, 'EMIT', 'EXIT'], c='(--)')

colon('DIGIT-CHAR?', ['doLIT', ord('0'), 'doLIT', ord('9') + 1, 'WITHIN', 'EXIT'], c='( c -- f )')

colon('D3@', [], c='( a -- u )')
dw(['DUP', 'C@', 'doLIT', ord('0'), '-', 'doLIT', 10, '*'])
dw(['OVER', 'CELL+', 'C@', 'doLIT', ord('0'), '-', '+', 'doLIT', 10, '*'])
dw(['SWAP', 'CELL+', 'CELL+', 'C@', 'doLIT', ord('0'), '-', '+', 'EXIT'])

colon('DEC3?', [], c='( a -- f )')
dw(['DUP', 'C@', 'DIGIT-CHAR?'])
dw(['OVER', 'CELL+', 'C@', 'DIGIT-CHAR?', 'AND'])
dw(['OVER', 'CELL+', 'CELL+', 'C@', 'DIGIT-CHAR?', 'AND'])
dw(['?branch', 'DEC3BAD'])
dw(['D3@', 'doLIT', 256, 'U<', 'EXIT'])
label('DEC3BAD')
dw(['DROP', 'doLIT', 0, 'EXIT'])

colon('CELL7?', [], c='( a -- f )')
dw(['DUP', 'C@', 'DUP', 'doLIT', 32, 'doLIT', 127, 'WITHIN', 'SWAP', 'doLIT', ord('"'), 'XOR', 'AND'])
dw(['?branch', 'CELL7BAD'])
dw(['DUP', 'CELL+', 'DEC3?'])
dw(['?branch', 'CELL7BAD'])
dw(['doLIT', 4, '+', 'DEC3?', 'EXIT'])
label('CELL7BAD')
dw(['DROP', 'doLIT', 0, 'EXIT'])

colon('IMGERR', ['doLIT', -1], c='( -- )')
ds('abort"', 'bad image data')
dw(['EXIT'])

colon('IMG-CHECK', [], c='( b u -- )')
dw(['doLIT', 7, '/', 'doLIT', 1, '+', 'NEGATE', '>R'])
dw(['branch', 'IMGC2'])
label('IMGC1')
dw(['DUP', 'CELL7?', '?branch', 'IMGBAD'])
dw(['doLIT', 7, '+'])
label('IMGC2')
dw(['doNEXT', 'IMGC1', 'R>', 'DROP', 'DROP', 'EXIT'])
label('IMGBAD')
dw(['IMGERR'])

colon('ANSI-RESET', [], c='( -- )')
dw(['doLIT', 27, 'EMIT'])
ds('."|', '[0m')
dw(['EXIT'])

colon('EMIT-CELL7', [], c='( a -- a )')
dw(['DUP', 'C@', '>R'])
dw(['doLIT', 27, 'EMIT'])
ds('."|', '[38;5;')
dw(['CELL+', 'DUP', 'doLIT', 3, 'TYPE'])
ds('."|', ';48;5;')
dw(['doLIT', 3, '+', 'DUP', 'doLIT', 3, 'TYPE'])
dw(['doLIT', ord('m'), 'EMIT', 'R>', 'EMIT', 'doLIT', 3, '+', 'EXIT'])

colon('EMIT-ROW7', [], c='( a u -- a )')
dw(['doLIT', 1, '+', 'NEGATE', '>R'])
dw(['branch', 'EROW2'])
label('EROW1')
dw(['EMIT-CELL7'])
label('EROW2')
dw(['doNEXT', 'EROW1', 'R>', 'DROP', 'EXIT'])

colon('do$', [], compile_only=True, c='(-- a)')
dw(['R>', 'R@', 'R>', 'COUNT', '+'])
dw(['ALIGNED', '>R', 'SWAP', '>R', 'EXIT'])

colon('$"|', ['do$', 'EXIT'], compile_only=True, public=False, c='(-- a)')

colon('S"|', ['do$', 'COUNT', 'EXIT'], compile_only=True, public=False, c='(-- b u)')

colon('."|', ['do$', 'COUNT', 'TYPE', 'EXIT'], compile_only=True, public=False, c='(--)')

colon('%adv', ['DUP', '%mta', '+!', 'NEGATE', '%mtu', '+!', 'EXIT'], c='(u --)')

colon('%clr', ['doLIT', 0, '%mtl', '!', 'EXIT'], c='(--)')

colon('%end', ['doLIT', FMTB, '%mtl', '@', '+', 'EXIT'], c='(-- b)')

colon('%room', [], c='(u --)')
dw(['%mtl', '@', '+', 'doLIT', FMTBS + 1, 'U<'])
dw(['?branch', 'FROOM1'])
dw(['EXIT'])
label('FROOM1')
ds('abort"', 'format overflow')
dw(['THROW'])

colon('%appc', [], c='(ch --)')
dw(['doLIT', 1, '%room', '%end', 'C!', 'doLIT', 1, '%mtl', '+!', 'EXIT'])

colon('%appb', [], c='(b u --)')
dw(['DUP', '%room', '>R', '%end', 'R@', 'CMOVE', 'R>', '%mtl', '+!', 'EXIT'])

colon('%ret', ['doLIT', FMTB, '%mtl', '@', 'EXIT'], c='(-- b u)')

colon('HEX?', ['doLIT', 16, 'DIGIT?', 'EXIT'], c='(c -- u t)')

colon('ESCERR', ['doLIT', -1], c='( -- )')
ds('abort"', 'invalid escape')
dw(['THROW'])

colon('UNESCAPE', [], c='(b u -- b u)')
dw(['OVER', '%mta', '!', 'DUP', '%mtu', '!', 'DROP'])
dw(['doLIT', 0, '%mtl', '!'])
label('UESC0')
dw(['%mtu', '@'])
dw(['?branch', 'UESC9'])
dw(['%mta', '@', 'C@', 'DUP', 'doLIT', ord('\\'), 'XOR'])
dw(['?branch', 'UESC1'])
dw(['OVER', '%mtl', '@', '+', 'C!', 'doLIT', 1, '%mtl', '+!', 'doLIT', 1, '%adv'])
dw(['branch', 'UESC0'])
label('UESC1')
dw(['DROP'])
dw(['%mtu', '@', 'doLIT', 2, 'U<'])
dw(['?branch', 'UESC2'])
dw(['ESCERR'])
label('UESC2')
dw(['doLIT', 1, '%adv'])
dw(['%mta', '@', 'C@', 'DUP', 'doLIT', ord('n'), 'XOR'])
dw(['?branch', 'UESCN0'])
dw(['DUP', 'doLIT', ord('r'), 'XOR'])
dw(['?branch', 'UESCR0'])
dw(['DUP', 'doLIT', ord('t'), 'XOR'])
dw(['?branch', 'UESCT0'])
dw(['DUP', 'doLIT', ord('\\'), 'XOR'])
dw(['?branch', 'UESCB0'])
dw(['DUP', 'doLIT', ord('"'), 'XOR'])
dw(['?branch', 'UESCQ0'])
dw(['DUP', 'doLIT', ord('0'), 'XOR'])
dw(['?branch', 'UESCZ0'])
dw(['DUP', 'doLIT', ord('x'), 'XOR'])
dw(['?branch', 'UESCX0'])
dw(['DROP', 'ESCERR'])
label('UESCN0')
dw(['DROP', 'doLIT', LF, 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCR0')
dw(['DROP', 'doLIT', CRR, 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCT0')
dw(['DROP', 'doLIT', 9, 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCB0')
dw(['DROP', 'doLIT', ord('\\'), 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCQ0')
dw(['DROP', 'doLIT', ord('"'), 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCZ0')
dw(['DROP', 'doLIT', 0, 'doLIT', 1, '%adv', 'branch', 'UESCW'])
label('UESCX0')
dw(['DROP'])
dw(['%mtu', '@', 'doLIT', 3, 'U<'])
dw(['?branch', 'UESCXA'])
dw(['ESCERR'])
label('UESCXA')
dw(['%mta', '@', 'doLIT', 1, '+', 'C@', 'HEX?'])
dw(['?branch', 'UESCX1'])
dw(['>R'])
dw(['%mta', '@', 'doLIT', 2, '+', 'C@', 'HEX?'])
dw(['?branch', 'UESCX2'])
dw(['R>', 'doLIT', 16, '*', '+'])
dw(['doLIT', 3, '%adv'])
dw(['branch', 'UESCW'])
label('UESCX1')
dw(['DROP', 'ESCERR'])
label('UESCX2')
dw(['DROP', 'R>', 'DROP', 'ESCERR'])
label('UESCW')
dw(['OVER', '%mtl', '@', '+', 'C!', 'doLIT', 1, '%mtl', '+!'])
dw(['branch', 'UESC0'])
label('UESC9')
dw(['%mtl', '@', 'EXIT'])

# Parsing
colon('parse', [], c='(b u c -- b u delta ; <string>)')
dw(['tmp', '!', 'OVER', '>R', 'DUP'])
dw(['?branch', 'PARS8'])
dw(['doLIT', 1, '-', 'tmp', '@', 'BL', '='])
dw(['?branch', 'PARS3'])
dw(['NEGATE', '>R'])
label('PARS1')
dw(['BL', 'OVER', 'C@', '-', '0<', 'NOT'])
dw(['?branch', 'PARS2'])
dw(['doLIT', 1, '+'])
dw(['doNEXT', 'PARS1', 'R>', 'DROP'])
dw(['R>', 'DROP', 'doLIT', 0, 'DUP', 'EXIT'])
label('PARS2')
dw(['R>'])
label('PARS3')
dw(['OVER', 'SWAP'])
dw(['>R'])
label('PARS4')
dw(['tmp', '@', 'OVER', 'C@', '-', 'tmp', '@', 'BL', '='])
dw(['?branch', 'PARS5'])
dw(['0<'])
label('PARS5')
dw(['?branch', 'PARS6'])
dw(['doLIT', 1, '+'])
dw(['doNEXT', 'PARS4', 'R>', 'DROP'])
dw(['DUP', '>R'])
dw(['branch', 'PARS7'])
label('PARS6')
dw(['R>', 'DROP', 'DUP', 'doLIT', 1, '+', '>R'])
label('PARS7')
dw(['OVER', '-', 'R>', 'R>', '-', 'EXIT'])
label('PARS8')
dw(['OVER', 'R>', '-', 'EXIT'])

colon('PARSE', [], c='(c -- b u ; <string>)')
dw(['>R', 'TIB', '>IN', '@', '+', '#TIB', '@'])
dw(['>IN', '@', '-', 'R>', 'parse', '>IN', '+!', 'EXIT'])

colon('.(', ['doLIT', ord(')'), 'PARSE', 'TYPE', 'EXIT'], immediate=True, c='(--)')

colon('(', ['doLIT', ord(')'), 'PARSE', '2DROP', 'EXIT'], immediate=True, c='(--)')

colon('\\', ['#TIB', '@', '>IN', '!', 'EXIT'], immediate=True, c='(--)')

colon('CHAR', ['BL', 'PARSE', 'DROP', 'C@', 'EXIT'], c='(-- c)')

colon('TOKEN', [], c='(-- a ; <string>)')
dw(['>IN', '@', '#TIB', '@', 'U<'])
dw(['?branch', 'TOKN0'])
dw(['TIB', '#TIB', '@', '+', 'BL', 'SWAP', 'C!'])
dw(['TIB', '>IN', '@', '+', '#TIB', '@', '>IN', '@', '-', 'doLIT', 1, '+', 'BL', 'parse', '>IN', '+!'])
dw(['doLIT', LEX_LEN_MASK, 'MIN', 'TOKBUF', '@', 'OVER', '-', 'CELL-', 'PACK$', 'EXIT'])
label('TOKN0')
dw(['NULL$', 'EXIT'])

colon('WORD', ['PARSE', 'HERE', 'PACK$', 'EXIT'], c='(c -- a ; <string>)')

# Dictionary search
colon('COUNTED>LEX', [], compile_only=True, public=False, c='(na -- lex)')
dw(['DUP', 'C@', 'doLIT', LEX_LEN_MASK, 'AND', 'DUP'])
dw(['?branch', 'CLEX0'])
dw(['>R', 'DUP', 'R@', '+', 'C@', '<<9', 'SWAP', 'DROP', 'R>', 'OR', 'EXIT'])
label('CLEX0')
dw(['2DROP', 'doLIT', 0, 'EXIT'])

colon('NAME>', ['CELL+', 'DUP', '@', 'doLIT', LEX_LEN_MASK, 'AND', '+', 'CELL+', 'EXIT'], c='(a -- xt)')
colon('>BUCKET', [], compile_only=True, public=False, c='(c table -- a | 0)')
dw(['OVER', 'doLIT', 32, 'doLIT', 127, 'WITHIN'])
dw(['?branch', 'GTBK0'])
dw(['SWAP', 'doLIT', 32, '-', '+', 'EXIT'])
label('GTBK0')
dw(['2DROP', 'doLIT', 0, 'EXIT'])

colon('HEADER>NA', ['CELL+', 'EXIT'], compile_only=True, public=False, c='(a -- na)')
colon('NA>HEADER', ['CELL-', 'EXIT'], compile_only=True, public=False, c='(na -- a)')
colon('VOCAB>BUCKETS', ['@', 'EXIT'], compile_only=True, public=False, c='(va -- a)')

colon('SAME?', [], c='(a a u -- a a f \\ -0+)')
label('SAME0')
dw(['DUP'])
dw(['?branch', 'SAME2'])
dw(['>R'])
label('SAME1')
dw(['2DUP', 'C@', 'SWAP', 'C@', '-', '?DUP'])
dw(['?branch', 'SAME1A'])
dw(['R>', 'DROP', 'EXIT'])
label('SAME1A')
dw(['SWAP', 'CELL+', 'SWAP', 'CELL+'])
dw(['R>', 'doLIT', -1, '+'])
dw(['branch', 'SAME0'])
label('SAME2')
dw(['DROP', 'doLIT', 0, 'EXIT'])

begin_code('MATCH?', c='(a a u -- t)')
body(['DUP', '?branch'])
dw(['MATQ2'])
body(['>R'])
label('MATQ1')
body(['2DUP', 'C@', 'SWAP', 'C@', 'XOR', '?DUP', '?branch'])
dw(['MATQ1A'])
body(['R>', 'DROP', 'DROP', '2DROP', 'doLIT'])
dw(0)
body(['EXIT'])
label('MATQ1A')
body(['SWAP', 'CELL+', 'SWAP', 'CELL+', 'R>', 'doLIT'])
dw(-1)
body(['+', 'DUP', '?branch'])
dw(['MATQ3'])
body(['>R', 'branch'])
dw(['MATQ1'])
label('MATQ3')
body(['DROP', '2DROP', 'doLIT'])
dw(-1)
body(['EXIT'])
label('MATQ2')
body(['DROP', '2DROP', 'doLIT'])
dw(-1)
body(['EXIT'])
end_code(auto_next=False)

colon('FIND-ON', ['doLIT', -1, 'FIND_STATS', '!', 'EXIT'], c='(--)')
colon('FIND-OFF', ['doLIT', 0, 'FIND_STATS', '!', 'EXIT'], c='(--)')

colon('.FIND', [], c='(--)')
ds('."|', ' visits=')
dw(['FIND_VISITS', '@', '.'])
ds('."|', ' full=')
dw(['FIND_FULLS', '@', '.'])
ds('."|', ' hit=')
dw(['FIND_HIT', '@', '.', 'EXIT'])

colon('FIND-RUNTIME', [], compile_only=True, public=False, c='(a va -- xt na | a F)')
dw(['SWAP', 'DUP', 'FIND_TOKEN', '!', 'DUP', 'COUNTED>LEX', 'FIND_LEX', '!', 'DUP', 'CELL+', 'C@', 'FIND_CHAR', '!', 'DROP'])
dw(['DUP', 'VOCAB>BUCKETS', 'CURRENT', '@', 'VOCAB>BUCKETS', 'XOR'])
dw(['?branch', 'FRUN0'])
dw(['doLIT', 0, 'FIND_PRIVATE', '!', 'branch', 'FRUN1'])
label('FRUN0')
dw(['STATE', '@', 'FIND_PRIVATE', '!'])
label('FRUN1')
dw(['DUP', 'VOCAB>BUCKETS', 'FIND_BUCKET', '!'])
dw(['FIND_BUCKET', '@', '?branch', 'FRUN6'])
dw(['FIND_CHAR', '@', 'FIND_BUCKET', '@', '>BUCKET', 'DUP'])
dw(['?branch', 'FRUN6A'])
dw(['@', 'DUP'])
dw(['?branch', 'FRUN6A'])
dw(['BUCKET_HEAD', '!'])
label('FRUN1A')
dw(['BUCKET_HEAD', '@', 'HEADER>NA', 'DUP', '@', 'DUP', 'tmp', '!'])
dw(['doLIT', PRIVV, 'AND'])
dw(['?branch', 'FRUN1B'])
dw(['FIND_PRIVATE', '@', '?branch', 'FRUN3A'])
label('FRUN1B')
dw(['tmp', '@', 'doLIT', LEX_NAME_MASK, 'AND'])
dw(['FIND_LEX', '@', 'XOR'])
dw(['?branch', 'FRUN2'])
dw(['DROP', 'BUCKET_HEAD', '@', '@', 'DUP'])
dw(['?branch', 'FRUN6A1'])
dw(['BUCKET_HEAD', '!', 'branch', 'FRUN1A'])
label('FRUN6A1')
dw(['branch', 'FRUN6A'])
label('FRUN2')
dw(['FIND_TOKEN', '@', 'CELL+', 'OVER', 'CELL+', 'FIND_LEX', '@', 'doLIT', LEX_LEN_MASK, 'AND', 'MATCH?'])
dw(['?branch', 'FRUN3A'])
dw(['>R', 'DROP', 'BUCKET_HEAD', '@', 'NAME>', 'R>', 'EXIT'])
label('FRUN3A')
dw(['DROP'])
label('FRUN3')
dw(['BUCKET_HEAD', '@', '@', 'DUP'])
dw(['?branch', 'FRUN6A'])
dw(['BUCKET_HEAD', '!', 'branch', 'FRUN1A'])
label('FRUN6A')
dw(['DROP'])
label('FRUN6')
dw(['DROP', 'FIND_TOKEN', '@', 'doLIT', 0, 'EXIT'])

colon('FIND-DEBUG', [], compile_only=True, public=False, c='(a va -- xt na | a F)')
dw(['SWAP', 'DUP', 'FIND_TOKEN', '!', 'DUP', 'COUNTED>LEX', 'FIND_LEX', '!', 'DUP', 'CELL+', 'C@', 'FIND_CHAR', '!', 'DROP'])
dw(['FIND_STATS', '@', '?branch', 'FDBG0'])
dw(['doLIT', 0, 'FIND_VISITS', '!'])
dw(['doLIT', 0, 'FIND_FULLS', '!'])
dw(['doLIT', 0, 'FIND_HIT', '!'])
label('FDBG0')
dw(['DUP', 'VOCAB>BUCKETS', 'CURRENT', '@', 'VOCAB>BUCKETS', 'XOR'])
dw(['?branch', 'FDBG1'])
dw(['doLIT', 0, 'FIND_PRIVATE', '!', 'branch', 'FDBG2'])
label('FDBG1')
dw(['STATE', '@', 'FIND_PRIVATE', '!'])
label('FDBG2')
dw(['DUP', 'VOCAB>BUCKETS', 'FIND_BUCKET', '!'])
dw(['FIND_BUCKET', '@', '?branch', 'FDBG9'])
dw(['FIND_CHAR', '@', 'FIND_BUCKET', '@', '>BUCKET', 'DUP'])
dw(['?branch', 'FDBG8'])
dw(['@', 'DUP'])
dw(['?branch', 'FDBG8'])
dw(['BUCKET_HEAD', '!'])
label('FDBG3')
dw(['FIND_STATS', '@', '?branch', 'FDBG3A'])
dw(['doLIT', 1, 'FIND_VISITS', '+!'])
label('FDBG3A')
dw(['BUCKET_HEAD', '@', 'HEADER>NA', 'DUP', '@', 'DUP', 'tmp', '!'])
dw(['doLIT', PRIVV, 'AND'])
dw(['?branch', 'FDBG4'])
dw(['FIND_PRIVATE', '@', '?branch', 'FDBG7'])
label('FDBG4')
dw(['tmp', '@', 'doLIT', LEX_NAME_MASK, 'AND'])
dw(['FIND_LEX', '@', 'XOR'])
dw(['?branch', 'FDBG5'])
dw(['DROP', 'BUCKET_HEAD', '@', '@', 'DUP'])
dw(['?branch', 'FDBG8A'])
dw(['BUCKET_HEAD', '!', 'branch', 'FDBG3'])
label('FDBG8A')
dw(['branch', 'FDBG8'])
label('FDBG5')
dw(['FIND_STATS', '@', '?branch', 'FDBG5A'])
dw(['doLIT', 1, 'FIND_FULLS', '+!'])
label('FDBG5A')
dw(['FIND_TOKEN', '@', 'CELL+', 'OVER', 'CELL+', 'FIND_LEX', '@', 'doLIT', LEX_LEN_MASK, 'AND', 'MATCH?'])
dw(['?branch', 'FDBG7'])
dw(['FIND_STATS', '@', '?branch', 'FDBG6'])
dw(['FIND_VISITS', '@', 'FIND_HIT', '!'])
label('FDBG6')
dw(['>R', 'DROP', 'BUCKET_HEAD', '@', 'NAME>', 'R>', 'EXIT'])
label('FDBG7')
dw(['DROP'])
dw(['BUCKET_HEAD', '@', '@', 'DUP'])
dw(['?branch', 'FDBG8'])
dw(['BUCKET_HEAD', '!', 'branch', 'FDBG3'])
label('FDBG8')
dw(['DROP'])
label('FDBG9')
dw(['DROP', 'FIND_TOKEN', '@', 'doLIT', 0, 'EXIT'])

colon('find', ["'FIND", '@', '>R', 'EXIT'], compile_only=True, public=False, c='(a va -- xt na | a F)')

colon('FIND-VOCS', [], compile_only=True, public=False, c='(a va -- xt na | a F)')
label('FDVC0')
dw(['DUP', '?branch', 'FDVC2'])
dw(['>R', 'DUP', 'R@', 'find', '?DUP'])
dw(['?branch', 'FDVC1'])
dw(['ROT', 'DROP', 'R>', 'DROP', 'EXIT'])
label('FDVC1')
dw(['DROP', 'R>', 'CELL+', '@', 'branch', 'FDVC0'])
label('FDVC2')
dw(['DROP', 'doLIT', 0, 'EXIT'])

colon('NAME?', [], compile_only=True, public=False, c='(a -- xt na | a F)')
dw(['CONTEXT', '@', 'FIND-VOCS', 'EXIT'])

colon('PROFILE-FIND', [], c='(-- ; <string>)')
dw(['doLIT', 'FIND-DEBUG', "'FIND", '!'])
dw(['FIND-ON'])
dw(['TOKEN', 'NAME?', '?DUP'])
dw(['?branch', 'PFND0'])
dw(['2DROP', 'branch', 'PFND1'])
label('PFND0')
dw(['DROP'])
label('PFND1')
dw(['.FIND'])
dw(['FIND-OFF'])
dw(['doLIT', 'FIND-RUNTIME', "'FIND", '!', 'EXIT'])

# Terminal
colon('^H', [], c='(b b b -- b b b)')
dw(['>R', 'OVER', 'R>', 'SWAP', 'OVER', 'XOR'])
dw(['?branch', 'BACK1'])
dw(['doLIT', BKSPP, 'EMIT'])
dw(['doLIT', 1, '-']) # From eForth86
dw(['doLIT', ord(' '), 'EMIT'])
dw(['doLIT', BKSPP, 'EMIT'])
label('BACK1')
dw(['EXIT'])

colon('XOFF', [], c='(-- )')
dw(['doLIT', 19, 'EMIT', 'EXIT'])

colon('XON', [], c='(-- )')
dw(['doLIT', 17, 'EMIT', 'EXIT'])

colon('TAP', [], c='(bot eot cur c -- bot eot cur)')
dw(['DUP', 'EMIT', 'OVER', 'C!'])
dw(['doLIT', 1, '+', 'EXIT'])

colon('kTAP', [], c='(bot eot cur c -- bot eot cur)')
dw(['DUP', 'doLIT', LF, 'XOR'])
dw(['?branch', 'KTAP0'])
dw(['DUP', 'doLIT', CRR, 'XOR'])
dw(['?branch', 'KTAP2'])
dw(['doLIT', BKSPP, 'XOR'])
dw(['?branch', 'KTAP1'])
dw(['TAP', 'EXIT'])
label('KTAP0')
dw(['DROP', 'EXIT'])
label('KTAP1')
dw(['^H', 'EXIT'])
label('KTAP2')
dw(['XOFF', 'DROP', 'SWAP', 'DROP', 'DUP', 'EXIT'])

colon('accept', [], c='(b u -- b u)')
dw(['OVER', '+', 'OVER'])
label('ACCP1')
dw(['2DUP', 'XOR'])
dw(['?branch', 'ACCP4'])
dw(['KEY', 'DUP', 'BL', 'doLIT', 127, 'WITHIN']) # eForth86
dw(['?branch', 'ACCP2'])
dw(['TAP'])
dw(['branch', 'ACCP3'])
label('ACCP2')
dw(['kTAP'])
label('ACCP3')
dw(['branch', 'ACCP1'])
label('ACCP4')
dw(['DROP', 'OVER', '-', 'EXIT'])

colon('EXPECT', ['accept', 'SPAN', '!', 'DROP', 'EXIT'], c='(b u --)')

colon('QUERY', [], c='(--)')
dw(['TIB', 'doLIT', TIBS, 'EXPECT', 'SPAN', '@', '#TIB', '!'])
dw(['XON', 'doLIT', 0, '>IN', '!', 'EXIT'])

# Error handling
colon('CATCH', [], c='(ca -- err#/0)')
dw(['SP@', '>R'])
dw(['HANDLER', '@', '>R'])
dw(['RP@', 'HANDLER', '!'])
dw(['doLIT', 'CATCH1', '>R', '>R', 'EXIT'])
label('CATCH1')
dw(['R>', 'HANDLER', '!'])
dw(['R>', 'DROP'])
dw(['doLIT', 0, 'EXIT'])

colon('THROW', [], c='(err# -- err#)')
dw(['HANDLER', '@', 'RP!'])
dw(['R>', 'HANDLER', '!'])
dw(['R>', 'SWAP', '>R'])
dw(['SP!'])
dw(['DROP'])
dw(['R>', 'EXIT'])

# Text interpreter
colon('?NUMHEAD', [], compile_only=True, public=False, c='(a -- a f)')
dw(['DUP', 'CELL+', '@', 'DUP', '>R'])
dw(['doLIT', ord('0'), 'doLIT', ord('9') + 1, 'WITHIN'])
dw(['R@', 'doLIT', ord('-'), '=', 'OR'])
dw(['R@', 'doLIT', ord('+'), '=', 'OR'])
dw(['R@', 'doLIT', ord('$'), '=', 'OR'])
dw(['BASE', '@', 'doLIT', 16, 'XOR'])
dw(['?branch', 'NUMH1'])
dw(['R>', 'DROP', 'EXIT'])
label('NUMH1')
dw(['R@', 'HEX?'])
dw(['SWAP', 'DROP', 'OR'])
dw(['R>', 'DROP', 'EXIT'])

colon('$INTERPRET', [], c='(a --)')
dw(['?NUMHEAD'])
dw(['?branch', 'INTE0'])
dw(['NUMBER?'])
dw(['?branch', 'INTE0'])
dw(['EXIT'])
label('INTE0')
dw(['NAME?', '?DUP'])
dw(['?branch', 'INTE1'])
dw(['@', 'doLIT', COMPO, 'AND'])
ds('abort"', ' compile only')
dw(['>R', 'EXIT'])
label('INTE1')
dw(['NUMBER?'])
dw(['?branch', 'INTE2'])
dw(['EXIT'])
label('INTE2')
dw(['THROW'])

colon('.OK', [], c='(--)')
dw(['STATE', '@'])
dw(['?branch', 'DOTO0'])
dw(['branch', 'DOTO1'])
label('DOTO0')
ds('."|', ' ok')
label('DOTO1')
dw(['CR', 'EXIT'])

colon('?STACK', ['DEPTH', '0<'], c='(--)')
ds('abort"', ' underflow')
dw(['EXIT'])

colon('EVAL', [], c='(--)')
label('EVAL1')
dw(['TOKEN', 'DUP', 'C@'])
dw(['?branch', 'EVAL2'])
dw(['STATE', '@'])
dw(['?branch', 'EVALI'])
dw(['$COMPILE'])
dw(['branch', 'EVAL1'])
label('EVALI')
dw(['LINE-RESET', 'INTERPRET,', 'LINE-RUN'])
dw(['branch', 'EVAL1'])
label('EVAL2')
dw(['DROP', '.OK', 'EXIT'])

# Shell
colon('PRESET', ['doLIT', TIBB, '#TIB', 'CELL+', '!', 'LINE-RESET', 'EXIT'], c='(--)')

colon('xio', [], compile_only=True, public=False, c='(a a a --)')
dw(['doLIT', 'accept', "'EXPECT", '2!', "'ECHO", '2!', 'EXIT'])

colon('FILE', [], c='(--)')
dw(['doLIT', 'PACE', 'doLIT', 'DROP', 'doLIT', 'kTAP', 'xio', 'EXIT'])

colon('HAND', [], c='(--)')
dw(['doLIT', '.OK', 'doLIT', 'EMIT', 'doLIT', 'kTAP', 'xio', 'EXIT'])

stub('I/O', public=False, c='( -- a )')
body(['doLIT', 'IO_DATA', 'EXIT'])
label('IO_DATA')
dw(['?rx'])
dw(['tx!'])

#		Return address of a null string with zero count.
variable('NULL$', 0, public=False, c='( -- a )')

colon('CONSOLE', ['I/O', '2@', "'?KEY", '2!', 'HAND', 'EXIT'], c='(--)')

colon('R/O', ['doLIT', 0x01, 'EXIT'], c='( -- fam )')
colon('W/O', ['doLIT', 0x02, 'EXIT'], c='( -- fam )')
colon('R/W', ['doLIT', 0x03, 'EXIT'], c='( -- fam )')
colon('OPEN-FILE', ['HOPEN', 'EXIT'], c='( c-addr u fam -- fileid ior )')
colon('CREATE-FILE', ['HCREATE', 'EXIT'], c='( c-addr u fam -- fileid ior )')
colon('CLOSE-FILE', ['HCLOSE', 'EXIT'], c='( fileid -- ior )')
colon('READ-LINE', ['HREADLN', 'EXIT'], c='( c-addr u1 fileid -- u2 flag ior )')
colon('WRITE-LINE', ['HWRITELN', 'EXIT'], c='( c-addr u fileid -- ior )')
colon('FILE-POSITION', ['HTELL', 'EXIT'], c='( fileid -- ud ior )')
colon('REPOSITION-FILE', ['HSEEK', 'EXIT'], c='( ud fileid -- ior )')
colon('FILE-SIZE', ['HSIZE', 'EXIT'], c='( fileid -- ud ior )')
colon('FLUSH-FILE', ['HFLUSH', 'EXIT'], c='( fileid -- ior )')
colon('DELETE-FILE', ['HDELETE', 'EXIT'], c='( c-addr u -- ior )')
colon('RENAME-FILE', ['HRENAME', 'EXIT'], c='( c-addr1 u1 c-addr2 u2 -- ior )')

colon('INCLUDE-FILE', ['DROP', 'doLIT', -1, 'EXIT'], c='( fileid -- ior ) disabled for now')

colon('INCLUDED', ['2DROP', 'doLIT', -1, 'EXIT'], c='( c-addr u -- ior ) disabled for now')

colon('MODULE-SAVE', [], compile_only=True, public=False, c='(--)')
dw(['LAST', '@', 'MODULE_LAST', '!'])
dw(['CP', '@', 'MODULE_CP', '!'])
dw(['FORTHVOC', '@', 'MODULE_FORTHVOC', '!'])
dw(['FORTHVOC', 'CELL+', '@', 'MODULE_FORTHVOC', 'CELL+', '!'])
dw(['FORTHVOC', 'CELL+', 'CELL+', '@', 'MODULE_FORTHVOC', 'CELL+', 'CELL+', '!'])
dw(['CONTEXT', '@', 'MODULE_CONTEXT', '!'])
for i in range(VOCSS):
    dw(['CONTEXT'] + ['CELL+'] * (i + 1) + ['@', 'MODULE_CONTEXT'] + ['CELL+'] * (i + 1) + ['!'])
dw(['CURRENT', '@', 'MODULE_CURRENT', '!'])
dw(['CURRENT', 'CELL+', '@', 'MODULE_CURRENT', 'CELL+', '!'])
dw(['EXIT'])

colon('MODULE-RESTORE-ORDER', [], compile_only=True, public=False, c='(--)')
dw(['MODULE_CONTEXT', '@', 'CONTEXT', '!'])
for i in range(VOCSS):
    dw(['MODULE_CONTEXT'] + ['CELL+'] * (i + 1) + ['@', 'CONTEXT'] + ['CELL+'] * (i + 1) + ['!'])
dw(['MODULE_CURRENT', '@', 'CURRENT', '!'])
dw(['MODULE_CURRENT', 'CELL+', '@', 'CURRENT', 'CELL+', '!'])
dw(['EXIT'])

colon('MODULE-CLEAR', [], compile_only=True, public=False, c='(--)')
dw(['doLIT', 0, 'MODULE_ACTIVE', '!'])
dw(['doLIT', 0, 'MODULE_FAILED', '!'])
dw(['EXIT'])

colon('MODULE-ROLLBACK', [], compile_only=True, public=False, c='(--)')
dw(['MODULE_FORTHVOC', '@', 'FORTHVOC', '!'])
dw(['MODULE_FORTHVOC', 'CELL+', '@', 'FORTHVOC', 'CELL+', '!'])
dw(['MODULE_FORTHVOC', 'CELL+', 'CELL+', '@', 'FORTHVOC', 'CELL+', 'CELL+', '!'])
dw(['MODULE-RESTORE-ORDER'])
dw(['MODULE_LAST', '@', 'LAST', '!'])
dw(['MODULE_CP', '@', 'CP', '!'])
dw(['MODULE_CP', '@', 'REWIND-ALL-BUCKETS'])
dw(['doLIT', 0, 'MODULE_ACTIVE', '!'])
dw(['doLIT', -1, 'MODULE_FAILED', '!'])
dw(['EXIT'])

colon('QUIT', [], c='(--)')
# largely from eForth86
dw(['RP0', '@', 'RP!'])
label('QUIT1')
dw(['[']) # start interpreting
label('QUIT2')
dw(['RP0', '@', 'RP!'])
dw(['QUERY'])
dw(['MODULE_FAILED', '@'])
dw(['?branch', 'QUIT2A'])
dw(['MODULE-SKIP-LINE'])
dw(['branch', 'QUIT4'])
label('QUIT2A')
dw(['doLIT', 'EVAL', 'CATCH', '?DUP'])
dw(['?branch', 'QUIT2'])
dw(["'PROMPT", '@', 'SWAP', 'CONSOLE', 'NULL$', 'OVER', 'XOR'])
dw(['?branch', 'QUIT3'])
dw(['SPACE', 'COUNT', 'TYPE'])
ds('."|', " ? ")
label('QUIT3')
dw(['MODULE_ACTIVE', '@'])
dw(['?branch', 'QUIT3A'])
dw(['MODULE-ROLLBACK'])
label('QUIT3A')
dw(['doLIT', '.OK', 'XOR'])
dw(['?branch', 'QUIT4'])
dw(['doLIT', ERR, 'EMIT'])
label('QUIT4')
dw(['PRESET', 'XON'])
dw(['branch', 'QUIT1'])

# Interpreter and compiler
colon('[', ['doLIT', 0, 'STATE', '!', 'EXIT'], immediate=True, c='(--)')

colon(']', ['doLIT', 1, 'STATE', '!', 'EXIT'], c='(--)')

# Primitive compiler words
colon("'", [], c='(-- xt)')
dw(['TOKEN', 'NAME?', '?branch', 'TICK1'])
dw(['DROP', 'EXIT'])
label('TICK1')
dw(['THROW'])

constant('_doNEXT', _primitives['doNEXT']['opcode'], c='primitive opcode constant')
constant('_?branch', _primitives['?branch']['opcode'], c='primitive opcode constant')
constant('_branch', _primitives['branch']['opcode'], c='primitive opcode constant')

colon('ALLOT', ['CP', '+!', 'EXIT'], c='(n --)')

colon('[COMPILE]', ["'", ',', 'EXIT'], immediate=True, c='(-- ; <string>)')

colon('COMPILE', ['R>', 'DUP', '@', ',', 'CELL+', '>R', 'EXIT'], compile_only=True, c='(--)')

colon('LITERAL', ['COMPILE', 'doLIT', ',', 'EXIT'], immediate=True, c='(w --)')

colon('[CHAR]', ['CHAR', 'LITERAL', 'EXIT'], immediate=True, c='(-- c ; <char>)')

colon('$,"', ['doLIT', ord('"'), 'WORD', 'COUNT', '+', 'ALIGNED', 'CP', '!', 'EXIT'], c='(--)')

colon('ESC,"', ['HERE', 'PACK$', 'COUNT', '+', 'ALIGNED', 'CP', '!', 'EXIT'], c='(b u --)')

colon('RECURSE', ['LAST', '@', 'NAME>', ',', 'EXIT'], immediate=True, c='(--)')

# Structures
# From eForth86
colon('BEGIN',['HERE', 'EXIT'], immediate=True, c='( -- a )')
colon('FOR', ['COMPILE', 'NEGATE', 'COMPILE', '>R', 'HERE', 'EXIT'], immediate=True, c='( -- a )')
colon('NEXT', ['COMPILE', 'doNEXT', ',', 'COMPILE', 'R>', 'COMPILE', 'DROP', 'EXIT'], immediate=True, c='( a -- )')
colon('UNTIL', ['doLIT', _primitives['?branch']['opcode'], ',', ',', 'EXIT'], immediate=True, c='( a -- )')
colon('AGAIN', ['doLIT', _primitives['branch']['opcode'], ',', ',', 'EXIT'], immediate=True, c='( a -- )')
colon('IF', ['doLIT', _primitives['?branch']['opcode'], ',', 'HERE', 'doLIT', 0, ',', 'EXIT'], immediate=True, c='( -- a )')
colon('AHEAD', ['doLIT', _primitives['branch']['opcode'], ',', 'HERE', 'doLIT', 0, ',', 'EXIT'], immediate=True, c='( -- a )')
colon('REPEAT', ['AGAIN', 'HERE', 'SWAP', '!', 'EXIT'], immediate=True, c='( a a -- )')
colon('THEN', ['HERE', 'SWAP', '!', 'EXIT'], immediate=True, c='( a -- )')
colon('AFT', ['DROP', 'AHEAD', 'BEGIN', 'SWAP', 'EXIT'], immediate=True, c='( a -- a a )')
colon('ELSE', ['AHEAD', 'SWAP', 'THEN', 'EXIT'], immediate=True, c='( a -- a )')
colon('WHILE', ['IF', 'SWAP', 'EXIT'], immediate=True, c='( a -- a a )')

colon('CLEAR-BUCKET-TABLE', [], compile_only=True, public=False, c='(a --)')
dw(['doLIT', 95, 'NEGATE', '>R'])
label('CBKT0')
dw(['doLIT', 0, 'OVER', '!', 'CELL+'])
dw(['doNEXT', 'CBKT0', 'R>', 'DROP'])
dw(['DROP', 'EXIT'])

colon('COPY-BUCKET-TABLE', [], compile_only=True, public=False, c='(src dst --)')
dw(['FIND_BUCKET', '!', 'tmp', '!'])
dw(['doLIT', 95, 'NEGATE', '>R'])
label('CPBK0')
dw(['tmp', '@', '@', 'FIND_BUCKET', '@', '!'])
dw(['tmp', '@', 'CELL+', 'tmp', '!'])
dw(['FIND_BUCKET', '@', 'CELL+', 'FIND_BUCKET', '!'])
dw(['doNEXT', 'CPBK0', 'R>', 'DROP'])
dw(['EXIT'])

colon('REWIND-BUCKET-TABLE', [], compile_only=True, public=False, c='(cutoff a --)')
dw(['SWAP', 'tmp', '!', 'FIND_BUCKET', '!'])
dw(['doLIT', 95, 'NEGATE', '>R'])
label('RBKTL')
dw(['FIND_BUCKET', '@', '@', 'BUCKET_HEAD', '!'])
label('RBKT0')
dw(['BUCKET_HEAD', '@', 'DUP'])
dw(['?branch', 'RBKT2'])
dw(['DUP', 'tmp', '@', 'U<'])
dw(['?branch', 'RBKT1'])
dw(['FIND_BUCKET', '@', '!', 'FIND_BUCKET', '@', 'CELL+', 'FIND_BUCKET', '!', 'branch', 'RBKT3'])
label('RBKT1')
dw(['@', 'BUCKET_HEAD', '!', 'branch', 'RBKT0'])
label('RBKT2')
dw(['DROP', 'doLIT', 0, 'FIND_BUCKET', '@', '!', 'FIND_BUCKET', '@', 'CELL+', 'FIND_BUCKET', '!'])
label('RBKT3')
dw(['doNEXT', 'RBKTL', 'R>', 'DROP'])
dw(['EXIT'])

colon('REWIND-VOCAB-BUCKETS', [], compile_only=True, public=False, c='(cutoff va --)')
dw(['VOCAB>BUCKETS', '?DUP'])
dw(['?branch', 'RVBK0'])
dw(['REWIND-BUCKET-TABLE', 'EXIT'])
label('RVBK0')
dw(['DROP', 'EXIT'])

colon('REWIND-ALL-BUCKETS', [], compile_only=True, public=False, c='(cutoff --)')
dw(['FORTHVOC'])
label('RABK0')
dw(['DUP', '?branch', 'RABK1'])
dw(['OVER', 'OVER', 'REWIND-VOCAB-BUCKETS'])
dw(['CELL+', '@', 'branch', 'RABK0'])
label('RABK1')
dw(['2DROP', 'EXIT'])

colon('INIT-FORTH-BUCKETS', [], compile_only=True, public=False, c='(--)')
dw(['doLIT', 'FORTH_BUCKET_SEED_ROM', 'doLIT', FORTH_BUCKET_HEADS_RAM, 'COPY-BUCKET-TABLE'])
dw(['doLIT', FORTH_BUCKET_HEADS_RAM, 'FORTHVOC', '!', 'EXIT'])

#		Conditional abort with an error message.
colon('ABORT"', [], immediate=True, c='(-- ; <string>)')
dw(['COMPILE','abort"', '$,"', 'EXIT'])

#		Run time routine of ABORT" . Abort with a message.
colon('abort"', [], compile_only=True, public=False, c='( f -- )')
dw(['?branch', 'ABOR1'])		#text flag
dw(['do$', 'THROW'])		  #pass error string
label('ABOR1')
dw(['do$', 'DROP', 'EXIT'])		#drop error

#		Compile an inline string literal.
colon('$"', ['COMPILE', '$"|', '$,"', 'EXIT'], immediate=True, c='(-- ; <string>)')

#		Compile an inline string literal, or type it immediately in interpret mode.
colon('."', [], immediate=True, c='(-- ; <string>)')
dw(['STATE', '@', '?branch', 'DQI1'])
dw(['doLIT', ord('"'), 'PARSE', 'UNESCAPE', 'COMPILE', '."|', 'ESC,"', 'EXIT'])
label('DQI1')
dw(['doLIT', ord('"'), 'PARSE', 'UNESCAPE', 'TYPE', 'EXIT'])

#		Compile or interpret a string literal as (addr len).
colon('S"', [], immediate=True, c='(-- b u ; <string>)')
dw(['STATE', '@', '?branch', 'SQI1'])
dw(['doLIT', ord('"'), 'PARSE', 'UNESCAPE', 'COMPILE', 'S"|', 'ESC,"', 'EXIT'])
label('SQI1')
dw(['doLIT', ord('"'), 'PARSE', 'UNESCAPE', 'EXIT'])

# String helpers
colon('U<=', ['doLIT', 1, '+', 'U<', 'EXIT'], c='(u1 u2 -- t)')

colon('?TARGET', [], c='(-- na ; <string>)')
dw(['TOKEN', 'DUP', 'C@'])
dw(['?branch', 'QTG1'])
dw(['EXIT'])
label('QTG1')
ds('$"|', ' name')
dw(['THROW'])

colon('FINDXT', [], compile_only=True, public=False, c='(na -- na xt t | na f)')
dw(['DUP', 'NAME?', '?DUP'])
dw(['?branch', 'FDXT1'])
dw(['DROP', 'doLIT', -1, 'EXIT'])
label('FDXT1')
dw(['DROP', 'doLIT', 0, 'EXIT'])

colon('STRING-BUILD', [], compile_only=True, c='(n na -- xt)')
dw(['OVER', '0<'])
dw(['?branch', 'STRB0'])
ds('abort"', 'negative capacity')
dw(['THROW'])
label('STRB0')
dw(['SWAP', '>R', 'HEADER', 'R>'])
dw(['HERE', 'doLIT', 6, '+', 'DUP', 'tmp', '!', 'DROP'])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw(['tmp', '@', 'doLIT', 2, '+', ','])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw(['tmp', '@', 'doLIT', 1, '+', ','])
dw(['doLIT', _primitives['@']['opcode'], ','])
dw(['doLIT', _primitives['EXIT']['opcode'], ','])
dw(['DUP', ',', 'doLIT', 0, ',', 'ALLOT'])
dw(['REVEAL', 'LAST', '@', 'NAME>', 'EXIT'])

colon('STR?', [], public=False, c='(xt -- xt t | f)')
dw(['DUP', '@', 'doLIT', _primitives['doLIT']['opcode'], 'XOR'])
dw(['?branch', 'STRQ1'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('STRQ1')
dw(['DUP', 'CELL+', '@', 'tmp', '!'])
dw(['DUP', 'CELL+', 'CELL+', '@', 'doLIT', _primitives['doLIT']['opcode'], 'XOR'])
dw(['?branch', 'STRQ2'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('STRQ2')
dw(['DUP', 'CELL+', 'CELL+', 'CELL+', '@', 'tmp', '@', 'CELL-', 'XOR'])
dw(['?branch', 'STRQ3'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('STRQ3')
dw(['DUP', 'doLIT', 4, '+', '@', 'doLIT', _primitives['@']['opcode'], 'XOR'])
dw(['?branch', 'STRQ4'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('STRQ4')
dw(['DUP', 'doLIT', 5, '+', '@', 'doLIT', _primitives['EXIT']['opcode'], 'XOR'])
dw(['?branch', 'STRQ5'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('STRQ5')
dw(['doLIT', -1, 'EXIT'])

colon('>STRBUF', [], public=False, c='(xt -- b)')
dw(['STR?', '?branch', 'SBF1', 'CELL+', '@', 'EXIT'])
label('SBF1')
ds('abort"', 'not string')
dw(['THROW'])

colon('>STRLENA', [], public=False, c='(xt -- a)')
dw(['STR?', '?branch', 'SLA1', 'CELL+', 'CELL+', 'CELL+', '@', 'EXIT'])
label('SLA1')
ds('abort"', 'not string')
dw(['THROW'])

colon('>STRCAP', ['>STRLENA', 'CELL-', '@', 'EXIT'], public=False, c='(xt -- n)')
colon('>STRLEN', ['>STRLENA', '@', 'EXIT'], public=False, c='(xt -- n)')

colon('STRCLR-XT', ['>STRLENA', 'doLIT', 0, 'SWAP', '!', 'EXIT'], public=False, c='(xt --)')
colon('STRCAP-XT', ['>STRCAP', 'EXIT'], public=False, c='(xt -- n)')

colon('STRSET-XT', [], public=False, c='(b u xt --)')
dw(['STRX', '!', 'DUP', 'STRX', '@', '>STRCAP', 'U<='])
dw(['?branch', 'SSET1'])
dw(['DUP', '>R', 'OVER', 'STRX', '@', '>STRBUF', 'R@', 'CMOVE', 'R>', 'DROP'])
dw(['SWAP', 'DROP', 'STRX', '@', '>STRLENA', '!', 'EXIT'])
label('SSET1')
ds('abort"', 'string overflow')
dw(['THROW'])

colon('STRSETN-XT', [], public=False, c='(b u n xt --)')
dw(['STRX', '!', 'DUP', 'STRX', '@', '>STRCAP', 'XOR'])
dw(['?branch', 'SSTN0'])
ds('abort"', 'capacity mismatch')
dw(['THROW'])
label('SSTN0')
dw(['DUP', 'doLIT', 1, '+', 'U<'])
dw(['?branch', 'SSTN1'])
dw(['STRX', '@', 'STRSET-XT', 'EXIT'])
label('SSTN1')
ds('abort"', 'string overflow')
dw(['THROW'])

colon('STRAPP-XT', [], public=False, c='(b u xt --)')
dw(['STRX', '!'])
dw(['%mta', '!', '%mtu', '!'])
dw(['%clr'])
dw(['STRX', '@', '>STRBUF', 'STRX', '@', '>STRLEN', '%appb'])
dw(['%mta', '@', '%mtu', '@', '%appb'])
dw(['%ret', 'STRX', '@', 'STRSET-XT', 'EXIT'])

colon('STRPRE-XT', [], public=False, c='(b u xt --)')
dw(['STRX', '!'])
dw(['%mta', '!', '%mtu', '!'])
dw(['%clr'])
dw(['%mta', '@', '%mtu', '@', '%appb'])
dw(['STRX', '@', '>STRBUF', 'STRX', '@', '>STRLEN', '%appb'])
dw(['%ret', 'STRX', '@', 'STRSET-XT', 'EXIT'])

colon('STRCAPP-XT', [], public=False, c='(ch xt --)')
dw(['STRX', '!'])
dw(['%clr'])
dw(['STRX', '@', '>STRBUF', 'STRX', '@', '>STRLEN', '%appb'])
dw(['%appc'])
dw(['%ret', 'STRX', '@', 'STRSET-XT', 'EXIT'])

colon('STRCHAR!-XT', [], public=False, c='(ch idx xt --)')
dw(['>R', 'DUP', '0<'])
dw(['?branch', 'SCHW0'])
ds('abort"', 'invalid index')
dw(['THROW'])
label('SCHW0')
dw(['DUP', 'R@', '>STRLEN', 'U<'])
dw(['?branch', 'SCHW1'])
dw(['R@', '>STRBUF', '+', 'C!', 'R>', 'DROP', 'EXIT'])
label('SCHW1')
ds('abort"', 'invalid index')
dw(['THROW'])

colon('LEN', ['SWAP', 'DROP', 'EXIT'], c='(b u -- u)')

colon('EMPTY?', [], c='(b u -- t)')
dw(['SWAP', 'DROP', '?DUP'])
dw(['?branch', 'EMP1'])
dw(['DROP', 'doLIT', 0, 'EXIT'])
label('EMP1')
dw(['doLIT', -1, 'EXIT'])

colon('STR=', [], c='(b u b u -- t)')
dw(['>R', 'OVER', 'R@', 'XOR'])
dw(['?branch', 'STRE1'])
dw(['R>', 'DROP', '2DROP', 'DROP', 'doLIT', 0, 'EXIT'])
label('STRE1')
dw(['SWAP', 'R>', 'DROP', 'MATCH?', 'EXIT'])

colon('STR<>', ['STR=', 'NOT', 'EXIT'], c='(b u b u -- t)')

colon('LEFT', [], c='(b u n -- b n)')
dw(['DUP', '0<'])
dw(['?branch', 'LEFT0'])
ds('abort"', 'invalid range')
dw(['THROW'])
label('LEFT0')
dw(['tmp', '!'])
dw(['tmp', '@', 'OVER', 'U<='])
dw(['?branch', 'LEFT1'])
dw(['DROP', 'tmp', '@', 'EXIT'])
label('LEFT1')
ds('abort"', 'invalid range')
dw(['THROW'])

colon('RIGHT', [], c='(b u n -- b n)')
dw(['DUP', '0<'])
dw(['?branch', 'RGHT0'])
ds('abort"', 'invalid range')
dw(['THROW'])
label('RGHT0')
dw(['DUP', 'OVER', 'U<='])
dw(['?branch', 'RGHT1'])
dw(['>R', 'SWAP', 'OVER', 'R@', '-', '+', 'R>', 'ROT', 'DROP', 'EXIT'])
label('RGHT1')
ds('abort"', 'invalid range')
dw(['THROW'])

colon('SUBSTR', [], c='(b u start count -- b u)')
dw(['>R', 'DUP', '0<'])
dw(['?branch', 'SUB0'])
ds('abort"', 'invalid range')
dw(['THROW'])
label('SUB0')
dw(['R@', '0<'])
dw(['?branch', 'SUB1'])
ds('abort"', 'invalid range')
dw(['THROW'])
label('SUB1')
dw(['tmp', '!'])
dw(['tmp', '@', 'OVER', 'U<='])
dw(['?branch', 'SUB2'])
dw(['tmp', '@', 'R@', '+', 'OVER', 'U<='])
dw(['?branch', 'SUB2'])
dw(['DROP', 'tmp', '@', '+', 'R>', 'EXIT'])
label('SUB2')
ds('abort"', 'invalid range')
dw(['THROW'])

colon('CHAR@', [], c='(b u idx -- ch)')
dw(['DUP', '0<'])
dw(['?branch', 'CHRAT0'])
ds('abort"', 'invalid index')
dw(['THROW'])
label('CHRAT0')
dw(['DUP', 'OVER', 'U<'])
dw(['?branch', 'CHRAT1'])
dw(['SWAP', 'DROP', '+', 'C@', 'EXIT'])
label('CHRAT1')
ds('abort"', 'invalid index')
dw(['THROW'])

# Parsing-string words
colon('STRING', [], immediate=True, c='(n -- ; <name>)')
dw(['STATE', '@'])
dw(['?branch', 'PSTR0'])
ds('abort"', 'STRING compile-state unsupported')
dw(['THROW'])
label('PSTR0')
dw(['?TARGET', 'FINDXT', '?branch', 'PSTR1'])
dw(['2DROP', 'DROP'])
ds('abort"', 'duplicate name')
dw(['THROW'])
label('PSTR1')
dw(['STRING-BUILD', 'DROP', 'EXIT'])

colon('TOSTR', [], immediate=True, c='(b u -- ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'TSTR0'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'TSTRI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRSET-XT', 'EXIT'])
label('TSTRI')
dw(['STRX', '@', 'STRSET-XT', 'EXIT'])
label('TSTR0')
dw(['STATE', '@'])
dw(['?branch', 'TSTR1'])
ds('abort"', 'missing string target')
dw(['THROW'])
label('TSTR1')
dw(['>R', 'OVER', '%mta', '!', 'DUP', '%mtu', '!', 'DUP', 'R>', 'STRING-BUILD', 'STRX', '!'])
dw(['%mta', '@', '%mtu', '@', 'STRX', '@', 'STRSET-XT', 'EXIT'])

colon('TOSTRN', [], immediate=True, c='(b u n -- ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'TSTN0'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'TSTNI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRSETN-XT', 'EXIT'])
label('TSTNI')
dw(['STRX', '@', 'STRSETN-XT', 'EXIT'])
label('TSTN0')
dw(['STATE', '@'])
dw(['?branch', 'TSTN1'])
ds('abort"', 'missing string target')
dw(['THROW'])
label('TSTN1')
dw(['>R', 'DUP', '%mtw', '!', 'ROT', 'DUP', '%mta', '!', 'ROT', 'DUP', '%mtu', '!', 'ROT'])
dw(['DUP', 'R>', 'STRING-BUILD', 'STRX', '!'])
dw(['%mta', '@', '%mtu', '@', '%mtw', '@', 'STRX', '@', 'STRSETN-XT', 'EXIT'])

colon('CLEAR', [], immediate=True, c='(-- ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'CLER1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'CLERI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRCLR-XT', 'EXIT'])
label('CLERI')
dw(['STRX', '@', 'STRCLR-XT', 'EXIT'])
label('CLER1')
ds('abort"', 'missing string target')
dw(['THROW'])

colon('CAPACITY', [], immediate=True, c='(-- n ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'CAP1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'CAPI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRCAP-XT', 'EXIT'])
label('CAPI')
dw(['STRX', '@', 'STRCAP-XT', 'EXIT'])
label('CAP1')
ds('abort"', 'missing string target')
dw(['THROW'])

colon('APPEND', [], immediate=True, c='(b u -- ; <name>)')
dw(['STATE', '@', '?branch', 'APPI0'])
dw(['?TARGET', 'FINDXT', '?branch', 'APP1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRAPP-XT', 'EXIT'])
label('APPI0')
dw(['%mta', '!', '%mtu', '!'])
dw(['?TARGET', 'FINDXT', '?branch', 'APP1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
label('APPI')
dw(['%mta', '@', '%mtu', '@'])
dw(['STRX', '@', 'STRAPP-XT', 'EXIT'])
label('APP1')
ds('abort"', 'missing string target')
dw(['THROW'])

colon('PREPEND', [], immediate=True, c='(b u -- ; <name>)')
dw(['STATE', '@', '?branch', 'PREI0'])
dw(['?TARGET', 'FINDXT', '?branch', 'PRE1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRPRE-XT', 'EXIT'])
label('PREI0')
dw(['%mta', '!', '%mtu', '!'])
dw(['?TARGET', 'FINDXT', '?branch', 'PRE1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
label('PREI')
dw(['%mta', '@', '%mtu', '@'])
dw(['STRX', '@', 'STRPRE-XT', 'EXIT'])
label('PRE1')
ds('abort"', 'missing string target')
dw(['THROW'])

colon('CAPPEND', [], immediate=True, c='(ch -- ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'CAPA1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'CAPAI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRCAPP-XT', 'EXIT'])
label('CAPAI')
dw(['STRX', '@', 'STRCAPP-XT', 'EXIT'])
label('CAPA1')
ds('abort"', 'missing string target')
dw(['THROW'])

colon('CHAR!', [], immediate=True, c='(ch idx -- ; <name>)')
dw(['?TARGET', 'FINDXT', '?branch', 'CHST1'])
dw(['SWAP', 'DROP', 'STRX', '!'])
dw(['STATE', '@', '?branch', 'CHSTI'])
dw(['STRX', '@', 'LITERAL', 'COMPILE', 'STRCHAR!-XT', 'EXIT'])
label('CHSTI')
dw(['STRX', '@', 'STRCHAR!-XT', 'EXIT'])
label('CHST1')
ds('abort"', 'missing string target')
dw(['THROW'])

# Compiler

#		Display a warning message if the word already exists.
colon('?UNIQUE', ['EXIT'], public=False, c='(a -- a)')

#		Compile a snapshot restore for one user-state cell.
colon('SNAP,', [], compile_only=True, public=False, c='(a --)')
dw(['DUP', '@'])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw([','])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw(['DUP', ','])
dw(['doLIT', _primitives['!']['opcode'], ','])
dw(['DROP', 'EXIT'])

#		Compile a snapshot restore for an explicit value/target pair.
colon('SNAP-INTO,', [], compile_only=True, public=False, c='(w a --)')
dw(['>R'])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw([','])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw(['R>', ','])
dw(['doLIT', _primitives['!']['opcode'], ','])
dw(['EXIT'])

#		Build a conventional inline dictionary header using the string at na.
colon('HEADER', [], compile_only=True, public=False, c='(na --)')
dw(['DUP', 'C@'])
dw(['?branch', 'PNAM1'])
dw(['?UNIQUE'])
dw(['DUP', 'tmp', '!'])
dw(['HERE', 'DUP', 'LAST', '!'])
dw(['doLIT', 0, ','])
dw(['tmp', '@', 'COUNTED>LEX', ','])
dw(['tmp', '@', 'CELL+', 'HERE', 'tmp', '@', 'C@', 'doLIT', LEX_LEN_MASK, 'AND', 'CMOVE'])
dw(['tmp', '@', 'C@', 'doLIT', LEX_LEN_MASK, 'AND', 'ALLOT'])
dw(['2DROP', 'EXIT'])
label('PNAM1')
ds('$"|', ' name')
dw(['THROW'])

# FORTH Compiler

label('PRIMS')
for word, meta in _primitives.items():
    dw(len(word), c=f"primitive '{word}'")
    dw(word)
    dw(meta['opcode'], c=f"opcode {word}")
    dw(meta['operands'] or 0, c=f"operands {word}")
dw(0, c='end primitive table')

colon('PRIM?', [], compile_only=True, public=False, c='(a -- opcode operands t | a f)')
dw(['DUP', 'tmp', '!'])             # preserve token
dw(['DUP', 'CELL+', 'C@', 'FIND_CHAR', '!'])
dw(['DROP', 'doLIT', 'PRIMS'])
label('PRIM1')
dw(['DUP', 'C@'])
dw(['?branch', 'PRIM4'])
dw(['DUP', 'CELL+', 'C@', 'FIND_CHAR', '@', 'XOR'])
dw(['?branch', 'PRIM2'])
dw(['COUNT', '+', 'CELL+', 'CELL+', 'branch', 'PRIM1'])
label('PRIM2')
dw(['tmp', '@', 'SWAP', 'DUP', 'C@', 'SAME?'])
dw(['?branch', 'PRIM3'])
dw(['SWAP', 'DROP', 'COUNT', '+', 'CELL+', 'CELL+', 'branch', 'PRIM1'])
label('PRIM3')
dw(['SWAP', 'DROP', 'COUNT', '+', 'DUP', '@', 'SWAP', 'CELL+', '@', 'doLIT', -1, 'EXIT'])
label('PRIM4')
dw(['DROP', 'tmp', '@', 'doLIT', 0, 'EXIT'])

label('IPRIMS')
for word in ordered_primitives('interpreted'):
    dw(len(word), c=f"interpreted primitive '{word}'")
    dw(word)
    dw(_primitives[word]['opcode'], c=f"opcode {word}")
dw(0, c='end interpreted primitive table')

colon('IPRIM?', [], compile_only=True, public=False, c='(a -- p T | a F)')
dw(['DUP', 'tmp', '!'])
dw(['DUP', 'CELL+', 'C@', 'FIND_CHAR', '!'])
dw(['DROP', 'doLIT', 'IPRIMS'])
label('IPRM1')
dw(['DUP', 'C@'])
dw(['?branch', 'IPRM4'])
dw(['DUP', 'CELL+', 'C@', 'FIND_CHAR', '@', 'XOR'])
dw(['?branch', 'IPRM2'])
dw(['COUNT', '+', 'CELL+', 'branch', 'IPRM1'])
label('IPRM2')
dw(['DUP', 'C@', '>R'])
dw(['tmp', '@', 'CELL+', 'OVER', 'CELL+', 'R>', 'MATCH?'])
dw(['?branch', 'IPRM3'])
dw(['COUNT', '+', '@', 'doLIT', -1, 'EXIT'])
label('IPRM3')
dw(['COUNT', '+', 'CELL+', 'branch', 'IPRM1'])
label('IPRM4')
dw(['DROP', 'tmp', '@', 'doLIT', 0, 'EXIT'])

#		Compile next word to code dictionary as a token or literal.
colon('$COMPILE', [], compile_only=True, public=False, c='(a --)')
dw(['?NUMHEAD'])
dw(['?branch', 'SCOM0'])
dw(['NUMBER?'])
dw(['?branch', 'SCOM0'])
dw(['doLIT', 'doLIT', ',', ',', 'EXIT'])
label('SCOM0')
dw(['NAME?', '?DUP'])
dw(['?branch', 'SCOM2'])
dw(['DUP', '@', 'DUP', 'doLIT', IMEDD, 'AND'])
dw(['?branch', 'SCOM1'])
dw(['DROP', 'DROP', '>R', 'EXIT'])
label('SCOM1')
dw(['doLIT', PRIMM, 'AND'])
dw(['?branch', 'SCOM1A'])
dw(['DROP', '@', ',', 'EXIT'])
label('SCOM1A')
dw(['DROP', ',', 'EXIT'])
label('SCOM2')
dw(['NUMBER?'])
dw(['?branch', 'SCOM3'])
dw(['doLIT', 'doLIT', ',', ',', 'EXIT'])
label('SCOM3')
dw(['THROW'])

colon('INTERPRET,', [], compile_only=True, public=False, c='(a --)')
dw(['?NUMHEAD'])
dw(['?branch', 'ITOK0'])
dw(['NUMBER?'])
dw(['?branch', 'ITOK0'])
dw(['LINE-LIT', 'EXIT'])
label('ITOK0')
dw(['NAME?', '?DUP'])
dw(['?branch', 'ITOK1'])
dw(['DUP', '@', 'doLIT', COMPO, 'AND'])
ds('abort"', ' compile only')
dw(['OVER', 'doLIT', "'", 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['OVER', 'doLIT', ':', 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['OVER', 'doLIT', 'USER', 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['OVER', 'doLIT', 'CREATE', 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['OVER', 'doLIT', 'VARIABLE', 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['OVER', 'doLIT', 'SEE', 'XOR'])
dw(['?branch', 'ITOKX'])
dw(['DUP', '@', 'doLIT', PRIMM, 'AND'])
dw(['?branch', 'ITOK0A'])
dw(['DROP', '@', 'LINE,', 'EXIT'])
label('ITOK0A')
dw(['DROP', 'LINE,', 'EXIT'])
label('ITOKX')
dw(['DROP', '>R', 'EXIT'])
label('ITOK1')
dw(['THROW'])

#		Reveal the last built word by linking it into the current vocabulary.
colon('REVEAL', [], compile_only=True, public=False, c='(--)')
dw(['LAST', '@', 'DUP', '>R', 'HEADER>NA', 'CELL+', 'C@', 'CURRENT', '@', 'VOCAB>BUCKETS', '>BUCKET', '?DUP'])
dw(['?branch', 'RVL0'])
dw(['DUP', '@', 'R@', '!'])
dw(['R>', 'SWAP', '!', 'EXIT'])
label('RVL0')
dw(['R>', 'DROP', 'EXIT'])

#		Make the last compiled word an immediate word.
colon('IMMEDIATE', ['doLIT', IMEDD, 'LAST', '@', 'CELL+', 'DUP', '@', 'ROT', 'OR', 'SWAP', '!', 'EXIT'], immediate=True, c='(--)')

colon('PRIVATE', ['doLIT', PRIVV, 'LAST', '@', 'CELL+', 'DUP', '@', 'ROT', 'OR', 'SWAP', '!', 'EXIT'], c='(--)')

colon('COMPILE-ONLY', ['doLIT', COMPO, 'LAST', '@', 'CELL+', 'DUP', '@', 'ROT', 'OR', 'SWAP', '!', 'EXIT'], c='(--)')


# Defining words

#		Create a rollback marker for mutable dictionary state.
colon('MARKER', [], c='(-- ; <string>)')
dw(['STATE', '@'])
dw(['?branch', 'MARK0'])
ds('abort"', 'MARKER compile-state unsupported')
dw(['THROW'])
label('MARK0')
dw(['LAST', '@', 'tmp', '!'])
dw(['HERE', 'STRX', '!'])
dw(['TOKEN', 'HEADER'])
dw(['FORTHVOC', 'SNAP,'])
dw(['FORTHVOC', 'CELL+', 'SNAP,'])
dw(['FORTHVOC', 'CELL+', 'CELL+', 'SNAP,'])
dw(['CONTEXT', 'SNAP,'])
for i in range(VOCSS):
    dw(['CONTEXT'] + ['CELL+'] * (i + 1) + ['SNAP,'])
dw(['CURRENT', 'SNAP,'])
dw(['CURRENT', 'CELL+', 'SNAP,'])
dw(['tmp', '@', 'LAST', 'SNAP-INTO,'])
dw(['STRX', '@', 'CP', 'SNAP-INTO,'])
dw(['doLIT', _primitives['doLIT']['opcode'], ','])
dw(['STRX', '@', ','])
dw(['doLIT', 'REWIND-ALL-BUCKETS', ','])
dw(['CP', '@', 'REWIND-ALL-BUCKETS'])
dw(['doLIT', _primitives['EXIT']['opcode'], ','])
dw(['REVEAL', 'EXIT'])

#		Forget a runtime definition from the current chain only.
colon('FORGET', [], c='(-- ; <string>)')
dw(['STATE', '@'])
dw(['?branch', 'FGT0'])
ds('abort"', 'FORGET compile-state unsupported')
dw(['THROW'])
label('FGT0')
dw(['TOKEN', 'CURRENT', '@', 'find', '?DUP'])
dw(['?branch', 'FGT1'])
dw(['>R', '2DROP', 'R>'])
dw(['DUP', 'doLIT', CODER, 'U<'])
dw(['?branch', 'FGT2'])
ds('abort"', 'protected')
dw(['THROW'])
label('FGT2')
dw(['NA>HEADER', 'DUP', 'CP', '!'])
dw(['CURRENT', '@', 'REWIND-VOCAB-BUCKETS'])
dw(['EXIT'])
label('FGT1')
dw(['THROW'])

#		Compile a new user variable.
colon('USER', ['TOKEN', 'HEADER', 'COMPILE', 'doUSER', ',', 'REVEAL', 'EXIT'], c='(n -- ; <string>)')

#		Create a new vocabulary selector and record.
colon('VOCABULARY', [], c='(-- ; <string>)')
dw(['TOKEN', 'HEADER'])
dw(['HERE', 'doLIT', 3, '+', 'DUP', 'tmp', '!', 'DROP'])
dw(['COMPILE', 'doVOC'])
dw(['tmp', '@', ','])
dw(['doLIT', _primitives['EXIT']['opcode'], ','])
dw(['tmp', '@', 'doLIT', 3, '+', ','])
dw(['doLIT', 0, ','])
dw(['doLIT', 0, ','])
dw(['tmp', '@', 'doLIT', 3, '+', 'DUP', 'doLIT', 95, 'ALLOT', 'CLEAR-BUCKET-TABLE'])
dw(['FORTHVOC', 'CELL+', '@', 'tmp', '@', 'CELL+', '!'])
dw(['tmp', '@', 'FORTHVOC', 'CELL+', '!'])
dw(['REVEAL', 'EXIT'])

#		Make the active search vocabulary the current definition target.
colon('DEFINITIONS', [], c='(--)')
dw(['CONTEXT', '@', 'VOCAB>BUCKETS', 'CURRENT', 'CELL+', '!'])
dw(['CURRENT', 'CELL+', 'CURRENT', '!', 'EXIT'])

colon('MODULE', [], c='(-- ; <string>)')
dw(['STATE', '@'])
dw(['?branch', 'MOD0'])
ds('abort"', 'MODULE compile-state unsupported')
dw(['THROW'])
label('MOD0')
dw(['MODULE_ACTIVE', '@', 'MODULE_FAILED', '@', 'OR'])
dw(['?branch', 'MOD1'])
ds('abort"', 'module active')
dw(['THROW'])
label('MOD1')
dw(['MODULE-SAVE'])
dw(['doLIT', -1, 'MODULE_ACTIVE', '!'])
dw(['doLIT', 0, 'MODULE_FAILED', '!'])
dw(['EXIT'])

colon('END-MODULE', [], c='(--)')
dw(['STATE', '@'])
dw(['?branch', 'EMOD0'])
ds('abort"', 'END-MODULE compile-state unsupported')
dw(['THROW'])
label('EMOD0')
dw(['MODULE_ACTIVE', '@', 'MODULE_FAILED', '@', 'OR'])
dw(['?branch', 'EMOD2'])
dw(['MODULE-CLEAR', 'EXIT'])
label('EMOD2')
ds('abort"', 'no module')
dw(['THROW'])

#		Compile a new array entry without allocating code space.
colon('CREATE', ['TOKEN', 'HEADER', 'doLIT', _primitives['doVAR']['opcode'], ',', 'REVEAL', 'EXIT'], c='(-- ; <string>)')

#		Compile a new variable initialized to 0.
colon('VARIABLE', ['CREATE', 'doLIT', 0, ',', 'EXIT'], c='(-- ; <string>)')

colon('MODULE-SKIP-LINE', [], compile_only=True, public=False, c='(--)')
dw(['TOKEN', 'NAME?', '?branch', 'MSKL0'])
dw(['doLIT', 'END-MODULE', 'XOR', '?branch', 'MSKL1'])
dw(['EXIT'])
label('MSKL0')
dw(['DROP', 'EXIT'])
label('MSKL1')
dw(['MODULE-CLEAR', '.OK', 'EXIT'])

# Tools

#		Display a string. Filter non-printing characters.
colon('_TYPE', [], c='(b u --)')
dw(['branch', 'UTYP2'])
label('UTYP1')
dw(['SWAP', 'DUP', 'C@', '>CHAR', 'EMIT'])
dw(['doLIT', 1, '+', 'SWAP', 'doLIT', -1, '+'])
label('UTYP2')
dw(['DUP', '?branch', 'UTYP3'])
dw(['branch', 'UTYP1'])
label('UTYP3')
dw(['2DROP', 'EXIT'])

#		Dump u bytes from , leaving a+u on the stack.
colon('dm+', [], c='(b u -- b)')
dw(['OVER', 'doLIT', 4, 'U.R'])
dw(['SPACE', 'NEGATE', '>R'])
dw(['branch', 'PDUM2'])
label('PDUM1')
dw(['DUP', 'C@', 'doLIT', 3, 'U.R'])
dw(['doLIT', 1, '+'])
label('PDUM2')
dw(['doNEXT', 'PDUM1', 'R>', 'DROP'])
dw(['EXIT'])

#		Dump u bytes from a, in a formatted manner.
colon('DUMP', [], c='(b u --)')
dw(['BASE', '@', '>R', 'HEX'])
dw(['doLIT', 16, '/'])
dw(['NEGATE', '>R'])
label('DUMP1')
dw(['CR', 'doLIT', 16, '2DUP', 'dm+'])
dw(['ROT', 'ROT'])
dw(['doLIT', 2, 'SPACES', '_TYPE'])
dw(['NUF?', 'NOT'])
dw(['?branch', 'DUMP2'])
dw(['doNEXT', 'DUMP1', 'R>', 'DROP'])
dw(['branch', 'DUMP3'])
label('DUMP2')
dw(['R>', 'DROP'])
label('DUMP3')
dw(['DROP', 'R>', 'BASE', '!', 'EXIT'])

# Stack tools

#		Display the contents of the data stack.
colon('.S', [], c='(--)')
dw(['CR','DEPTH'])		  #stack depth
dw(['?DUP'])
dw(['?branch', 'DOTS3Z'])
dw(['doLIT', 1, '+', 'NEGATE', '>R'])              # start count down loop
dw(['branch', 'DOTS2']) #skip first pass
label('DOTS1')
dw(['R@', 'NEGATE', 'doLIT', 1, '-', 'PICK', '.']) # index stack from bottom to top
label('DOTS2')
dw(['doNEXT', 'DOTS1', 'R>', 'DROP'])   #loop till done
label('DOTS3')
ds('."|', ' <sp')
dw(['EXIT'])
label('DOTS3Z')
dw(['branch', 'DOTS3'])

colon('.BASE', ['BASE', '@', 'DECIMAL', 'DUP', '.', 'BASE', '!', 'EXIT'], c='(--)')
colon('.FREE', ['SP0', '@', 'CP', '@', '-', 'U.', 'EXIT'], c='(--)')

#		Save stack pointer in CSP for error checking.
colon('!CSP', ['SP@', 'CSP', '!', 'EXIT'], c='(--)')

#		Abort if stack pointer differs from that saved in CSP.
colon('?CSP', [], c='(--)')
dw(['SP@', 'CSP', '@', 'XOR'])
ds('abort"', 'stack depth error')
dw(['EXIT'])

#		Convert code address to a name address.
colon('XT>NAME-IN-VOC', [], compile_only=True, public=False, c='(xt va -- na | 0)')
dw(['SWAP', 'tmp', '!'])
dw(['VOCAB>BUCKETS', '?DUP'])
dw(['?branch', 'XTNV4'])
dw(['doLIT', 95, 'NEGATE', '>R'])
label('XTNVL')
dw(['DUP', '@', 'BUCKET_HEAD', '!'])
label('XTNV0')
dw(['BUCKET_HEAD', '@', 'DUP'])
dw(['?branch', 'XTNV2'])
dw(['DUP', 'NAME>', 'tmp', '@', 'XOR'])
dw(['?branch', 'XTNV1'])
dw(['@', 'BUCKET_HEAD', '!', 'branch', 'XTNV0'])
label('XTNV1')
dw(['DROP', 'BUCKET_HEAD', '@', 'HEADER>NA', 'SWAP', 'DROP', 'R>', 'DROP', 'EXIT'])
label('XTNV2')
dw(['DROP', 'CELL+'])
dw(['doNEXT', 'XTNVL', 'R>', 'DROP'])
dw(['DROP'])
label('XTNV4')
dw(['doLIT', 0, 'EXIT'])

colon('>NAME', [], public=False, c='(xt -- na | F)')
dw(['FORTHVOC'])
label('TNAM1')
dw(['DUP'])
dw(['?branch', 'TNAM4'])
dw(['OVER', 'OVER', 'XT>NAME-IN-VOC', '?DUP'])
dw(['?branch', 'TNAM2'])
dw(['SWAP', 'DROP', 'SWAP', 'DROP', 'EXIT'])
label('TNAM2')
dw(['SWAP', 'DROP', 'CELL+', '@', 'branch', 'TNAM1'])
label('TNAM4')
dw(['DROP', 'doLIT', 0, 'EXIT'])

colon('P>NAME', [], public=False, c='(p -- na | F)')
dw(['doLIT', 'PRIMS'])
label('P2NM0')
dw(['DUP', 'C@'])
dw(['?branch', 'P2NM2'])
dw(['2DUP', 'COUNT', '+', '@', 'XOR'])
dw(['?branch', 'P2NM1'])
dw(['COUNT', '+', 'CELL+', 'CELL+', 'branch', 'P2NM0'])
label('P2NM1')
dw(['SWAP', 'DROP', 'EXIT'])
label('P2NM2')
dw(['SWAP', 'DROP', 'EXIT'])

colon('P>OPS', [], public=False, c='(p -- u)')
dw(['doLIT', 'PRIMS'])
label('P2OP0')
dw(['DUP', 'C@'])
dw(['?branch', 'P2OP2'])
dw(['2DUP', 'COUNT', '+', '@', 'XOR'])
dw(['?branch', 'P2OP1'])
dw(['COUNT', '+', 'CELL+', 'CELL+', 'branch', 'P2OP0'])
label('P2OP1')
dw(['SWAP', 'DROP', 'COUNT', '+', 'CELL+', '@', 'EXIT'])
label('P2OP2')
dw(['SWAP', 'DROP', 'doLIT', 0, 'EXIT'])

#		Display the name at address.
colon('.ID', [], c='(a --)')
dw(['?DUP'])
dw(['?branch', 'DOTI1'])
dw(['COUNT', 'doLIT', 0x1F, 'AND'])
dw(['_TYPE', 'EXIT'])
label('DOTI1')
ds('."|', '{noName}')
dw(['EXIT'])

#		A simple decompiler.
colon('SEE', [], c='(-- ; <string>)')
dw(['TOKEN', 'NAME?', 'DUP', '?branch', 'SEE0'])
dw(['DROP', 'CR'])
label('SEE1')
dw(['DUP', '@', 'DUP', 'tmp', '!', 'DUP'])
dw(['doLIT', XT_BASE, 'U<'])
dw(['?branch', 'SEE2'])
dw(['P>NAME'])
dw(['branch', 'SEE2A'])
label('SEE2')
dw(['>NAME'])
label('SEE2A')
dw(['?DUP'])
dw(['?branch', 'SEE3'])
dw(['SPACE', '.ID'])
dw(['branch', 'SEE4'])
label('SEE3')
dw(['U.'])
label('SEE4')
dw(['tmp', '@', 'doLIT', XT_BASE, 'U<'])
dw(['?branch', 'SEE4XT'])
dw(['tmp', '@', 'doLIT', 'EXIT', 'XOR'])
dw(['?branch', 'SEE5'])
dw(['tmp', '@', 'P>OPS', '?DUP'])
dw(['?branch', 'SEE4XT'])
dw(['DROP'])
label('SEE4A')
dw(['NUF?'])
dw(['?branch', 'SEE4B'])
dw(['branch', 'SEE5'])
label('SEE4B')
dw(['CELL+', 'DUP', '@', 'U.', 'CELL+'])
dw(['NUF?'])
dw(['?branch', 'SEE1'])
dw(['branch', 'SEE5'])
label('SEE4XT')
dw(['CELL+'])
dw(['NUF?'])
dw(['?branch', 'SEE1'])
label('SEE5')
dw(['DROP', 'EXIT'])
label('SEE0')
dw(['THROW'])

#		Display the names in the context vocabulary.
colon('WORDS', [], c='(--)')
dw(['CR', 'CONTEXT', '@', 'VOCAB>BUCKETS', '?DUP'])
dw(['?branch', 'WORS4'])
dw(['doLIT', 95, 'NEGATE', '>R'])
label('WORSL')
dw(['DUP', '@', 'BUCKET_HEAD', '!'])
label('WORS1')
dw(['BUCKET_HEAD', '@', 'DUP'])
dw(['?branch', 'WORS3'])
dw(['HEADER>NA', 'DUP', '@', 'doLIT', COMPO, 'AND'])
dw(['?branch', 'WORS1B'])
dw(['DROP', 'BUCKET_HEAD', '@', '@', 'BUCKET_HEAD', '!', 'branch', 'WORS1'])
label('WORS1B')
dw(['DUP', '@', 'doLIT', PRIVV, 'AND'])
dw(['?branch', 'WORS1A'])
dw(['DROP', 'BUCKET_HEAD', '@', '@', 'BUCKET_HEAD', '!', 'branch', 'WORS1'])
label('WORS1A')
dw(['DUP', 'SPACE', '.ID', 'DROP', 'BUCKET_HEAD', '@', '@', 'BUCKET_HEAD', '!', 'NUF?'])
dw(['?branch', 'WORS1'])
dw(['DROP', 'DROP', 'EXIT'])
label('WORS3')
dw(['DROP', 'CELL+'])
dw(['doNEXT', 'WORSL', 'R>', 'DROP'])
dw(['DROP'])
label('WORS4')
dw(['EXIT'])

# Hardware RESET

#		Return the version number of this implementation.
colon('VER', ['doLIT', VER*256+EXT, 'EXIT'], c='(-- u)')

#		Display the sign-on message of eForth.
colon('hi', [], c='(--)')
comment('ghost of !io removed; initialization retained as a no-op')
dw(['CR'])
ds('."|', f'PDR-16/XT Forth v{VER}.{EXT}')
dw(['CR'])
ds('."|', 'derived from eForth by C.H.Ting')
dw(['CR', 'EXIT'])


colon('EMPTY', [], c='(--)')
dw(['doLIT', CODER, 'CP', '!'])
dw(['doLIT', 'LASTN', 'LAST', '!'])
dw(['doLIT', 0, 'FORTHVOC', 'CELL+', '!'])
dw(['doLIT', CODER, 'REWIND-ALL-BUCKETS'])
dw(['FORTH', 'DEFINITIONS'])
dw(['EXIT'])

colon('CMOVE>', [], c='(b b u --)')
dw(['DUP', '?branch', 'CMVB3'])
dw(['>R', 'OVER', 'R@', '+', 'doLIT', 1, '-', 'OVER', 'R@', '+', 'doLIT', 1, '-', 'C@', 'SWAP', 'C!'])
dw(['R>', 'doLIT', -1, '+'])
dw(['branch', 'CMOVE>'])
label('CMVB3')
dw(['DROP', '2DROP', 'EXIT'])

colon('MOVE', [], c='(b b u --)')
dw(['2DUP', 'DROP', 'SWAP', 'U<'])
dw(['?branch', 'MOVE1'])
dw(['CMOVE', 'EXIT'])
label('MOVE1')
dw(['CMOVE>', 'EXIT'])

colon('COLD', [], c='(--)')
label('COLD1')
dw(['doLIT', SP0_INIT, 'SP!'])
dw(['doLIT', RP0_INIT, 'RP!'])
dw(['doLIT', UZERO,'doLIT',UPP]) 
dw(['doLIT', 2 * (ULAST-UZERO), 'CMOVE']) # initialize full user area (CMOVE count is byte-oriented)
dw(['doLIT', FORTH_BUCKET_HEADS_RAM, 'FORTHVOC', '!'])
dw(['doLIT', 0, 'FORTHVOC', 'CELL+', '!'])
dw(['PRESET']) # initialize stack and TIB 
dw(['hi']) # application boot 
dw(['doLIT', 'LASTN', 'LAST', '!'])
dw(['FORTH','DEFINITIONS']) # initialize search order
dw(['.OK']) # report ready state on startup
dw(['doLIT', SP0_INIT, 'SP!']) # start interactive interpretation with an empty data stack
dw(['QUIT']) # start interpretation 
dw(['branch', 'COLD1']) # just in case 

# Interpreted primitive shadows
#
# Keep these late in the seed so they stay near the top of the link chain.
# The list is ordered from colder to hotter lookup targets for the current
# live-compiled source set (01-image.fs, 07-math.fs, 03-fstrings.fs), so the
# words looked up most often end up nearest the head of the dictionary.
for word in ordered_primitives('shadow'):
    primitive(word, c='shadow primitive for interpreted execution')

# Compilation hot path
# Keep these late in the seed so they stay near the top of the link chain and
# are found quickly during source compilation. The definition order is chosen
# so the hottest words sit nearest the front of the dictionary.
# A few frequently used non-primitives are also redefined here with identical
# bodies so they can participate in the same lookup hot path without having to
# move their original bootstrap definitions earlier in the file.
colon(',', ['HERE', 'DUP', 'CELL+', 'CP', '!', '!', 'EXIT'], c='(w --)')
colon('ABS',       [], c='( n -- +n )')
dw(['DUP', '0<'])
dw(['?branch', 'HABS1'])
dw(['NEGATE'])
label('HABS1')
dw(['EXIT'])

colon("2DUP", ['OVER', 'OVER', 'EXIT'], c='( w1 w2 -- w1 w2 w1 w2 )')
colon("/", ["/MOD", "SWAP", "DROP", "EXIT"], c='( n n -- q )')
colon("-",   ['SUB', 'EXIT'], c='( w w -- w )')
colon('=',         [], c='( w w -- t )')
dw(['XOR'])
dw(['?branch', 'HEQU1'])
dw(['doLIT', 0, 'EXIT'])
label('HEQU1')
dw(['doLIT', -1, 'EXIT'])
colon('<>', ['=', 'NOT', 'EXIT'], c='( w w -- t )')
colon('>', ['SWAP', '<', 'EXIT'], c='( n1 n2 -- t )')
colon('<=', ['>', 'NOT', 'EXIT'], c='( n1 n2 -- t )')
colon('>=', ['<', 'NOT', 'EXIT'], c='( n1 n2 -- t )')

colon("+", ['U+', 'EXIT'], c='( w w -- w )')

colon(';', ['doLIT', _primitives['EXIT']['opcode'], ',', '[', 'REVEAL', 'EXIT'], immediate=True, compile_only=True, c='(--)')
colon(':', ['TOKEN', 'HEADER', ']', 'EXIT'], c='(-- ; <string>)')

# Seed the higher-level source libraries into the ROM dictionary after the
# compile hot path has been established.
emit_precompiled_01_image()
emit_precompiled_04_ansi()
emit_precompiled_07_math()
emit_precompiled_03_fstrings()
emit_precompiled_08_editor()

define('LASTN', link())
ROM_DICT_END = pc()
org(symbol('UZERO_FORTHVOC'))
dw(FORTH_BUCKET_HEADS_RAM, c='FORTHVOC bucket table ptr')
org(symbol('FORTH_BUCKET_HEADS_TEMPLATE'))
label('FORTH_BUCKET_SEED_ROM', c='Seed FORTH bucket table template')
for index, head in enumerate(seed_bucket_heads()):
    dw(head, c=f'FORTH bucket {index + 32}')
org(ROM_DICT_END)
define('ROM_END', ROM_DICT_END)

org(CODER)
label('CODER', c='Beginning of the runtime user dictionary in RAM')

org(SPP-STS-1)
label('Top_DS', c='Lower limit of data stack')

org(SPP)
label('SPP', c='Upper boundary of data stack')

org(TIBB)
label('TIBB', c='Start of The Input Buffer')

org(RPP-RTS-1)
label('Top_RS', c='Lower limit of return stack')

org(RPP)
label('RPP', c='Upper boundary of return stack')

org(UPP)
label('UPP', c='Start of user variable space')

org(EM)
label('EM', 'Just beyond end of memory')

end('eForth')
