# Makefile raiz para orquestrar build do SoC e compilação do firmware
# Uso:
#   make build-all CROSS_COMPILE=riscv32-unknown-elf-

CROSS_COMPILE ?= riscv32-unknown-elf-
PYTHON ?= python
BOARD ?= i9
REVISION ?= 7.2

.PHONY: help build-soc firmware build-all clean csr-table

help:
	@echo "Makefile de alto nível para este projeto"
	@echo "Targets:"
	@echo "  build-soc      - gera gateware com LiteX (requer toolchain FPGA: yosys/nextpnr/prjtrellis)"
	@echo "  headers-only   - gera apenas headers/CSRs (sem sintetizar gateware)"
	@echo "  sim            - compila e executa o testbench do acelerador (iverilog + vvp)"
	@echo "  firmware       - compila firmware em ip/ via ip/Makefile (requer headers gerados)"
	@echo "  build-all      - build-soc seguido de firmware"
	@echo "  clean          - limpa artefatos de firmware (ip/clean)"
	@echo "  load           - programa o bitstream gerado (usa openFPGALoader/ecpprog via script)"
	@echo "  prog-only      - somente programar bitstream existente (sem build)"
	@echo "  uart-log PORT=/dev/ttyUSB0 BAUD=115200 - captura a saída UART em docs/uart_log.txt"

build-soc:
	@echo "Verificando se LiteX está disponível..."
	@$(PYTHON) -c "import sys,pkgutil; (sys.exit('LiteX não encontrado. Instale litex no seu ambiente.') if pkgutil.find_loader('litex') is None else print('LiteX disponível'))"
	@echo "Iniciando build do SoC (ip/build_soc.py --build)"
	@$(PYTHON) ip/build_soc.py --board $(BOARD) --revision $(REVISION) --build

firmware:
	@echo "Compilando firmware (ip/Makefile)..."
	@$(MAKE) -C ip CROSS_COMPILE=$(CROSS_COMPILE) all || (echo "Falha ao compilar firmware. Verifique CROSS_COMPILE e se os headers gerados existem."; exit 1)

build-all: build-soc firmware
	@echo "Build completo: SoC + firmware"

clean:
	@$(MAKE) -C ip clean || true

csr-table:
	@echo "Gerando tabela de CSRs (dotp) a partir de build/dotp/csr.csv..."
	@$(PYTHON) ip/gen_csr_table.py > build/dotp/csr_table.md || (echo "Falha ao gerar tabela. Verifique se csr.csv existe."; exit 1)
