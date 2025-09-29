/* Linker script mínimo para firmware RISC-V (32-bit, ilp32)
   Ajuste conforme sua toolchain/board. Coloca .text em 0x10000000 por convenção LiteX
*/
ENTRY(_start)

SECTIONS
{
  /* SRAM base conforme regiões padrão do LiteX deste SoC */
  . = 0x10000000;

  .init : { KEEP(*(.init)) }

  .text : {
    KEEP(*(.text*))
    KEEP(*(.rodata*))
  }

  .data : {
    KEEP(*(.data*))
  }

  .bss : {
    . = ALIGN(4);
    KEEP(*(.bss*))
    KEEP(*(COMMON))
  }

  . = ALIGN(8);
  _stack_top = . + 0x2000; /* 8 KiB de stack por padrão */
}
