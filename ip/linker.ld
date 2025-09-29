/* Linker script mínimo para firmware RISC-V (32-bit, ilp32)
   Ajuste conforme sua toolchain/board. Coloca .text em 0x10000000 por convenção LiteX
*/
ENTRY(_start)

SECTIONS
{
  . = 0x10000000;
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
}
