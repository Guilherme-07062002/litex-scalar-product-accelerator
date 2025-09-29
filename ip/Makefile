# Makefile para compilar o firmware do acelerador de produto escalar
# Uso:
# make CROSS_COMPILE=riscv32-unknown-elf- all
# Dependências: toolchain RISC-V (gcc, objcopy)

CROSS_COMPILE ?= riscv32-unknown-elf-
CC      := $(CROSS_COMPILE)gcc
OBJCOPY := $(CROSS_COMPILE)objcopy

BUILD_DIR := build
INCLUDE := ../build/dotp/software/include/generated
SRC := crt0.s firmware_dotp.c
OUT_ELF := $(BUILD_DIR)/firmware.elf
OUT_BIN := $(BUILD_DIR)/firmware.bin

CFLAGS := -O2 -march=rv32imac -mabi=ilp32 -Wall -Wextra -I$(INCLUDE) -I$(INCLUDE)/.. -I../.venv/lib/python3.12/site-packages/litex/soc/software/include -I.
LDFLAGS := -T linker.ld

.PHONY: all clean

all: $(OUT_ELF) $(OUT_BIN)

$(OUT_ELF): $(SRC)
	@mkdir -p $(BUILD_DIR)
	@if [ ! -d "$(INCLUDE)" ]; then echo "ERROR: headers not found. Run the SoC build first to generate csr.h: python -m ip.soc_dot_product --build"; exit 1; fi
	$(CC) $(CFLAGS) -nostdlib -o $@ $^ $(LDFLAGS)

$(OUT_BIN): $(OUT_ELF)
	$(OBJCOPY) -O binary $< $@

clean:
	rm -rf $(BUILD_DIR)
