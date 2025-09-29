# Makefile raiz para orquestrar build do SoC e compilação do firmware
# Uso:
#   make build-all CROSS_COMPILE=riscv32-unknown-elf-

CROSS_COMPILE ?= riscv32-unknown-elf-
PYTHON ?= python

.PHONY: help build-soc firmware build-all clean

help:
	@echo "Makefile de alto nível para este projeto"
	@echo "Targets:"
	@echo "  build-soc      - roda ip/build_soc.py --build (requer LiteX)"
	@echo "  firmware       - compila firmware em ip/ via ip/Makefile (requer headers gerados)"
	@echo "  build-all      - build-soc seguido de firmware"
	@echo "  clean          - limpa artefatos de firmware (ip/clean)"

build-soc:
	@echo "Verificando se LiteX está disponível..."
	@$(PYTHON) - <<PY || (echo "LiteX não encontrado. Instale litex no seu ambiente."; exit 1)
try:
    import litex
    print('LiteX disponível')
except Exception as e:
    raise
PY
	@echo "Iniciando build do SoC (ip/build_soc.py --build)"
	@$(PYTHON) ip/build_soc.py --build

firmware:
	@echo "Compilando firmware (ip/Makefile)..."
	@$(MAKE) -C ip CROSS_COMPILE=$(CROSS_COMPILE) all || (echo "Falha ao compilar firmware. Verifique CROSS_COMPILE e se os headers gerados existem."; exit 1)

build-all: build-soc firmware
	@echo "Build completo: SoC + firmware"

clean:
	@$(MAKE) -C ip clean || true
