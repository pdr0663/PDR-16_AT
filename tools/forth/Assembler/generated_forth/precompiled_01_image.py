from asm import colon, comment, ds, dw, label, variable


def emit_precompiled_01_image() -> None:
    comment('precompiled from V4/Forth Sources/01-image.fs')

    colon('C,', [])
    dw(['HERE', 'DUP', 'CELL+', 'CP', '!', 'C!', 'EXIT'])

    colon('IMG-WIDTH', [])
    dw(['@', 'EXIT'])

    colon('IMG-HEIGHT', [])
    dw(['CELL+', '@', 'EXIT'])

    colon('IMG-DATA', [])
    dw(['doLIT', 2, '+', 'EXIT'])

    colon('IMG"', [], immediate=True)
    dw(['IMG-CELLS', '!', 'doLIT', 34, 'PARSE', '2DUP', 'SWAP', 'DROP', 'IMG-CELLS', '@', 'doLIT', 7, '*', 'XOR', '?branch', 'PC_01_2Dimage_IMG_22_IF_FALSE_1', 'IMGERR'])
    label('PC_01_2Dimage_IMG_22_IF_FALSE_1')
    dw(['2DUP', 'IMG-CHECK', 'HERE', '>R', '2DUP', 'SWAP', 'R>', 'ROT', 'CMOVE', 'ALLOT', 'DROP', 'EXIT'])

    colon('EMIT-IMAGE', [])
    dw(['DUP', 'IMG-WIDTH', 'IMGW', '!', 'DUP', 'IMG-HEIGHT', 'SWAP', 'IMG-DATA', 'SWAP'])
    label('PC_01_2Dimage_EMIT_2DIMAGE_BEGIN_1')
    dw(['DUP', '?branch', 'PC_01_2Dimage_EMIT_2DIMAGE_WHILE_END_2', 'SWAP', 'IMGW', '@', 'EMIT-ROW7', 'CR', 'SWAP', 'doLIT', 1, '-', 'branch', 'PC_01_2Dimage_EMIT_2DIMAGE_BEGIN_1'])
    label('PC_01_2Dimage_EMIT_2DIMAGE_WHILE_END_2')
    dw(['2DROP', 'ANSI-RESET', 'EXIT'])
