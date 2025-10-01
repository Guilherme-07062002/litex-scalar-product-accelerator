    .section .init
    .globl _start
_start:
    # Configura SP para topo da SRAM (definido no linker)
    la sp, _stack_top

    # Chama main()
    call main

1:
    j 1b
