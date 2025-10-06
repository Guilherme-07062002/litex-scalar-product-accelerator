BUILD_DIR ?= ../build/dotp
CROSS_COMPILE ?= riscv32-unknown-elf-

include $(BUILD_DIR)/software/include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

OBJECTS = crt0.o firmware_dotp.o

all: firmware.bin

firmware.elf: $(OBJECTS)
	$(CC) $(LDFLAGS) -T linker.ld -N -o $@ \
		$(OBJECTS) \
		$(PACKAGES:%=-L$(BUILD_DIR)/software/%) \
		-Wl,--gc-sections \
		-Wl,-Map,$@.map \
		$(LIBS:lib%=-l%)
	chmod -x $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@

crt0.o: crt0.s
	$(assemble)

firmware_dotp.o: firmware_dotp.c
	$(compile)

clean:
	$(RM) $(OBJECTS) firmware.elf firmware.bin .*~ *~
