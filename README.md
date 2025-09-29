# Tarefa 04 — SoC com LiteX: Acelerador de Produto Escalar via CSR

Este repositório contém a Tarefa 04 com um acelerador de produto escalar integrado ao LiteX:

- Acelerador de produto escalar 8×32 bits (signed) com resultado 64 bits.
- Wrapper LiteX com interface via CSR (a0..a7, b0..b7, start, done, result_lo/hi).
- Integração ao target Colorlight i5 (i9v7.2 compatível) usando LiteX.
- Firmware em C para envio de dados, acionamento do acelerador e comparação com software.

## Objetivo

Demonstrar a integração de um bloco SV customizado como periférico CSR em um SoC LiteX e compará-lo com a implementação em software via UART.

## Estrutura

```text
rtl/            Módulos RTL (acelerador de produto escalar)
tb/             Testbench do acelerador
sim/            Saída de simulação (VVP, VCD)
build/          Script de automação (menu)
doc/            (espaço para relatório/diagramas)
ip/             Wrapper LiteX, SoC Python e firmware C
```

## Novo módulo (tarefa 04)

`dot_product_accel.sv` Acelerador de produto escalar 8×32 (signed) → 64 bits, interface com `start/done` e inputs `a0..a7`, `b0..b7`. Implementação sequencial (8 ciclos) e testbench `tb_dot_product_accel.sv` com checagem automática.

## Execução (menu SV)

No Bash:

```bash
bash build/build.sh
```

O menu principal traz opções para rodar o testbench do acelerador e abrir ondas. VCD gerado: `sim/dot_product_accel.vcd`.

## Execução Direta (exemplos)

Produto escalar:

```bash
iverilog -g2012 -o sim/dot_product_accel.vvp rtl/dot_product_accel.sv tb/tb_dot_product_accel.sv && vvp sim/dot_product_accel.vvp
```

Abrir ondas (se GTKWave instalado):

```bash
gtkwave sim/dot_product_accel.vcd &
```


## SoC LiteX + Acelerador via CSR

Arquivos principais:

- `ip/dot_product_wrapper.py`: wrapper LiteX/Migen, exporta registradores CSR e instancia `rtl/dot_product_accel.sv`.
- `ip/soc_dot_product.py`: SoC baseado no target Colorlight i5, adiciona o periférico e gera `csr.h` para o firmware.
- `ip/firmware_dotp.c`: firmware em C que escreve os vetores, aciona `start`, espera `done` e lê `result` (comparando com software).

### Mapa de CSR (resumo)

Base do periférico: definida automaticamente pelo LiteX; ver `build/dotp/csr.csv`.

- write: `dotp_a0..a7`, `dotp_b0..b7`, `dotp_start`.
- read:  `dotp_done.done`, `dotp_result_lo`, `dotp_result_hi`.

### Requisitos/Dependências

- Python 3.8+
- LiteX, Migen, toolchain ECP5 (yosys+nextpnr-ecp5+prjtrellis)
- litex-boards

Instalação (referência oficial):

- <https://github.com/enjoy-digital/litex>
- <https://github.com/litex-hub/litex-boards>

## Instalação rápida (exemplos)

As instruções a seguir são orientativas — adapte à sua distribuição e preferências. Recomenda-se usar um ambiente virtual Python.

Linux (exemplo, Ubuntu/Debian):

```bash
# Dependências do sistema (exemplo)
sudo apt update
sudo apt install -y build-essential git python3 python3-pip python3-venv \
	gcc-multilib g++-multilib libffi-dev libssl-dev

# Criar e ativar virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Instalar LiteX e litex-boards via pip (modo rápido)
pip install --upgrade pip
pip install litex litex-boards

# Instalar toolchain RISC-V (opcional; pode usar toolchains pré-compiladas)
# Exemplo: riscv32-unknown-elf toolchain via apt (pode não existir em todas distros)
# Alternativa: baixar pré-compilado em https://github.com/riscv/riscv-gnu-toolchain/releases
```

Windows (WSL ou Git Bash recomendado):

Use WSL (Ubuntu) para seguir as instruções Linux acima. Em ambientes Windows nativos, instale uma toolchain RISC-V para Windows e garanta que `riscv32-unknown-elf-gcc` esteja no PATH.

ECP5 FPGA toolchain (para síntese/bitstream):

Siga as instruções das ferramentas open-source:

- yosys: https://github.com/YosysHQ/yosys
- nextpnr (ecp5): https://github.com/YosysHQ/nextpnr
- prjtrellis: https://github.com/olofk/prjtrellis

Para simplificar, consulte também os guias de instalação do LiteX e litex-boards (links acima).

### Build do SoC

Um script auxiliar foi adicionado para facilitar o build do SoC e a geração dos headers: `ip/build_soc.py`.

Exemplo (ambiente com LiteX instalado):

```bash
python ip/build_soc.py --build
```

Saídas relevantes esperadas:

- `build/dotp/csr.csv` e `build/dotp/software/include/generated/csr.h`
- Bitstream em `build/dotp/gateware/` (se a síntese for habilitada e as ferramentas estiverem presentes)

Para carregar (quando suportado no ambiente):

```bash
python ip/soc_dot_product.py --load
```

### Compilar/rodar firmware

Após o build do SoC, use o Makefile em `ip/` para compilar o firmware. Exemplo:

```bash
make -C ip CROSS_COMPILE=riscv32-unknown-elf-
```

O Makefile procura os headers gerados em `build/dotp/software/include/generated` e compila `ip/firmware_dotp.c` em `ip/build/firmware.elf` e `ip/build/firmware.bin`.

Execução: conectar via UART (serial) ao SoC; o firmware imprime os resultados de SW e HW e a verificação `[OK]`.

### Log de Execução (exemplo esperado)

```text
LiteX Dot-Product Accelerator Demo
CPU: VexRiscv
Software:  <valor>
Hardware:  <valor>
[OK] Resultado coincide!
```

Obs.: os valores dependem dos vetores de teste no firmware.

## Referências

- <https://github.com/enjoy-digital/litex>
- <https://github.com/enjoy-digital/litex/wiki>
- <https://github.com/enjoy-digital/litex/wiki/Tutorials-Resources>
- <https://www.controlpaths.com/2022/01/17/building-soc-litex/>
- <https://github.com/litex-hub/litex-boards>
- <https://github.com/litex-hub/fpga_101>
- <https://github.com/matheus-555/Projeto-Embarcatech-FPGA>
- <https://github.com/JN513/Utilizando-FPGAs-com-ferramentas-OpenSource>
- <https://www.youtube.com/watch?v=qPougRqk_SY>
