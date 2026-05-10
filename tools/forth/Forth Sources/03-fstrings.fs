\ 03-fstrings.fs
\ Formatted-string extensions source-built into the final ROM image.

: ~err -1 ABORT" bad f-string" ; PRIVATE

: ~pad
  0 MAX
  DUP
  IF
    1 - RECURSE
    BL %appc
  ELSE
    DROP
  THEN
; PRIVATE

: ~wtype %mtw @ OVER - ~pad %appb ; PRIVATE

: ~char
  DUP 256 U<
  IF
    EXIT
  THEN
  256 /MOD SWAP DROP
; PRIVATE

: ~next-char SWAP 1 + SWAP 1 - ; PRIVATE

: ~nzlen
  DUP
  IF
    OVER C@ ~char IF 1 ELSE 0 THEN >R
    ~next-char RECURSE
    R> +
  ELSE
    2DROP 0
  THEN
; PRIVATE

: ~appnz
  DUP
  IF
    OVER C@ ~char ?DUP IF %appc ELSE DROP THEN
    ~next-char RECURSE
  ELSE
    2DROP
  THEN
; PRIVATE

: ~wtype-nz
  2DUP ~nzlen
  %mtw @ SWAP - ~pad
  ~appnz
; PRIVATE

: ~xstr BASE @ >R HEX <# #S #> R> BASE ! ; PRIVATE

: ~pdigits
  DUP
  IF
    1 - >R
    #
    R> RECURSE
  ELSE
    DROP
  THEN
; PRIVATE

: ~pstr
  DUP >R ABS <# %mtp @ DUP
  IF
    ~pdigits
    46 HOLD
  ELSE
    DROP
  THEN
  #S R> SIGN #>
; PRIVATE

: ~outd
  %mtp @ 0<
  IF
    str ~wtype-nz
  ELSE
    ~pstr ~wtype-nz
  THEN
; PRIVATE

: ~outu
  %mtp @ 0<
  IF
    <# #S #> ~wtype-nz
  ELSE
    ~err
  THEN
; PRIVATE

: ~outx
  %mtp @ 0<
  IF
    ~xstr ~wtype-nz
  ELSE
    ~err
  THEN
; PRIVATE

: ~outc
  %mtp @ 0<
  IF
    %mtw @ 1 - ~pad %appc
  ELSE
    ~err
  THEN
; PRIVATE

: ~outs
  %mtp @ 0<
  IF
    ~wtype
  ELSE
    ~err
  THEN
; PRIVATE

: ~pow10
  DUP
  IF
    1 - RECURSE 10 *
  ELSE
    DROP 1
  THEN
; PRIVATE

: ~outa
  %mtp @ 0<
  IF
    0 %mtp !
  THEN
  %mtp @
  IF
    %mtp @ ~pow10 BIN>DEG.S
  ELSE
    BIN>DEG
  THEN
  ~outd
; PRIVATE

: ~c@ %mta @ C@ ; PRIVATE

: ~width-digits
  %mtu @
  IF
    ~c@ 48 58 WITHIN
    IF
      ~c@ 48 - %mtw @ 10 * + %mtw !
      1 %adv
      RECURSE
    THEN
  THEN
; PRIVATE

: ~prec-digits
  %mtu @
  IF
    ~c@ 48 58 WITHIN
    IF
      -1 %mtf !
      ~c@ 48 - %mtp @ 10 * + %mtp !
      1 %adv
      RECURSE
    THEN
  THEN
; PRIVATE

: ~default?
  ~c@ 125 =
; PRIVATE

: ~type-sa
  DUP 115 =
  IF
    DROP ~outs
  ELSE
    DUP 97 =
    IF
      DROP ~outa
    ELSE
      DROP ~err
    THEN
  THEN
; PRIVATE

: ~type-dispatch
  DUP 100 =
  IF
    DROP ~outd
  ELSE
    DUP 117 =
    IF
      DROP ~outu
    ELSE
      DUP 120 =
      IF
        DROP ~outx
      ELSE
        DUP 99 =
        IF
          DROP ~outc
        ELSE
          ~type-sa
        THEN
      THEN
    THEN
  THEN
; PRIVATE

: ~field-tail
  1 %adv
  %mtu @ ?DUP IF DROP ELSE ABORT" bad f-string" THEN
  ~c@ 125 XOR ABORT" bad f-string"
  1 %adv
  ~type-dispatch
; PRIVATE

: ~field
  1 %adv
  0 %mtw !
  -1 %mtp !
  %mtu @ ?DUP IF DROP ELSE ABORT" bad f-string" THEN
  ~default?
  IF
    1 %adv ~outd
  ELSE
    ~width-digits
    %mtu @ ?DUP IF DROP ELSE ABORT" bad f-string" THEN
    ~c@ 46 =
    IF
      1 %adv
      0 %mtp !
      0 %mtf !
      ~prec-digits
      %mtf @ ?DUP IF DROP ELSE ABORT" bad f-string" THEN
    THEN
    ~c@ DUP 125 =
    IF
      DROP 1 %adv ~outd
    ELSE
      ~field-tail
    THEN
  THEN
; PRIVATE

: ~eval-lbrace
  1 %mtu @ U<
  IF
    %mta @ 1 + C@ 123 =
    IF
      123 %appc 2 %adv
    ELSE
      ~field
    THEN
  ELSE
    ~field
  THEN
; PRIVATE

: ~eval-rbrace
  1 %mtu @ U<
  IF
    %mta @ 1 + C@ 125 =
    IF
      125 %appc 2 %adv
    ELSE
      ~err
    THEN
  ELSE
    ~err
  THEN
; PRIVATE

: ~eval
  2DUP DROP %mta !
  %mtu !
  DROP
  %clr
  BEGIN
    %mtu @
  WHILE
    ~c@ DUP 123 =
    IF
      DROP ~eval-lbrace
    ELSE
      DUP 125 =
      IF
        DROP ~eval-rbrace
      ELSE
        %appc 1 %adv
      THEN
    THEN
  REPEAT
  %ret
; PRIVATE

: ~run do$ COUNT ~eval ; COMPILE-ONLY

: ~"| ~run ; COMPILE-ONLY

: F"
  STATE @
  IF
    34 PARSE UNESCAPE COMPILE ~run ESC,"
  ELSE
    34 PARSE UNESCAPE ~eval
  THEN
;
IMMEDIATE
