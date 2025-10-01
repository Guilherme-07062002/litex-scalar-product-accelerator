# Makefile raiz para orquestrar build do SoC e compilação do firmware
# Uso:
#   make build-all CROSS_COMPILE=riscv32-unknown-elf-

CROSS_COMPILE ?= riscv32-unknown-elf-
PYTHON ?= python

.PHONY: help build-soc headers-only sim firmware build-all clean load prog-only

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

build-soc:
	@echo "Verificando se LiteX está disponível..."
	@$(PYTHON) -c "import litex; print('LiteX disponível')" || (echo "LiteX não encontrado. Instale litex no seu ambiente."; exit 1)
	@echo "Iniciando build do SoC (ip/soc_dot_product.py --build)"
	@$(PYTHON) ip/soc_dot_product.py --build

load:
	@echo "Programando bitstream (openFPGALoader/ecpprog)..."
	@$(PYTHON) ip/soc_dot_product.py --prog-only

prog-only: load

headers-only:
	@echo "Gerando apenas headers/CSRs (sem gateware)..."
	@$(PYTHON) ip/soc_dot_product.py --headers-only

sim:
	@echo "Compilando e executando testbench do acelerador (iverilog)..."
	@mkdir -p sim
	@iverilog -g2012 -o sim/dot_product_accel.vvp rtl/dot_product_accel.sv tb/tb_dot_product_accel.sv
	@vvp sim/dot_product_accel.vvp

firmware:
	@echo "Compilando firmware (ip/Makefile)..."
	@$(MAKE) -C ip CROSS_COMPILE=$(CROSS_COMPILE) all || (echo "Falha ao compilar firmware. Verifique CROSS_COMPILE e se os headers gerados existem."; exit 1)

build-all: build-soc firmware
	@echo "Build completo: SoC + firmware"

clean:
	@$(MAKE) -C ip clean || true
