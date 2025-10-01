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
- `ip/soc_dot_product.py`: SoC baseado no target Colorlight i5/i9 (padrão i9 rev 7.2), adiciona o periférico e gera `csr.h` para o firmware. Inclui suporte a gravação de bitstream via `openFPGALoader`/`ecpprog`.
- `ip/firmware_dotp.c`: firmware em C que escreve os vetores, aciona `start`, espera `done` e lê `result` (comparando com software).

### Como rodar (Makefile)

- Testbench do acelerador (RTL):

```
make sim
```

- Gerar apenas os headers/CSRs (sem sintetizar gateware):

```
make headers-only PYTHON=.venv/bin/python
```

- Compilar o firmware com a toolchain local do repositório:

```
make -C ip CROSS_COMPILE=../tools/bin/riscv32-unknown-elf- all
```

- (Opcional) Construir o SoC e gateware (requer yosys/nextpnr/prjtrellis):

```
make build-soc PYTHON=.venv/bin/python
```

- (Opcional) Carregar o bitstream gerado (requer openFPGALoader ou ecpprog):

```
make load PYTHON=.venv/bin/python
```

- (Opcional) Simular o firmware end-to-end sem FPGA:

```
.venv/bin/python ip/firmware_sim.py
```

### Mapa de CSR (resumo)

Base do periférico: definida automaticamente pelo LiteX; ver `build/dotp/csr.csv`.

- write: `dotp_a0..a7`, `dotp_b0..b7`, `dotp_start`.
- read:  `dotp_done.done`, `dotp_result_lo`, `dotp_result_hi`.

Endereços (exemplo gerado neste projeto):

- Base CSR: `0xF0000000`
- Offsets:
	- `a0..a7`  → `0x00 .. 0x1C`
	- `b0..b7`  → `0x20 .. 0x3C`
	- `start`   → `0x40`
	- `done`    → `0x44`
	- `result_lo` → `0x48`
	- `result_hi` → `0x4C`

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

Instalação rápida (oss-cad-suite) usando script auxiliar:

```
# Baixe a URL da release mais recente do oss-cad-suite
./tools/install_ecp5_toolchain.sh https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-12-20/oss-cad-suite-linux-x64-20241220.tgz
# Ative o ambiente
source tools/oss-cad-suite/environment
```

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

Você pode usar o alvo `make load` (que chama `ip/soc_dot_product.py --prog-only`) ou pedir para o script carregar após o build com `--load`. Por padrão, o script tenta detectar o bitstream em `build/dotp/gateware/` e usar `openFPGALoader -b colorlight -f <bit>`. Para usar `ecpprog` ou apontar um bitstream específico:

```
.venv/bin/python ip/soc_dot_product.py --build --load --loader ecpprog
.venv/bin/python ip/soc_dot_product.py --prog-only --bitstream build/dotp/gateware/top.bit
```

Target/revisão (conforme aulas): o padrão é Colorlight i9 rev 7.2. Para mudar:

```bash
.venv/bin/python ip/soc_dot_product.py --headers-only --board i5 --revision 7.0
# Para build completo (requer ferramentas FPGA):
.venv/bin/python ip/soc_dot_product.py --build --board i5 --revision 7.0

Clock padrão do SoC: 50 MHz. Para alterar via CLI:

```bash
.venv/bin/python ip/soc_dot_product.py --build --sys-clk-freq 60e6
```
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
Software: 0xFFFFFFFFFFFFFFF8
Hardware: 0xFFFFFFFFFFFFFFF8
[OK] Resultado coincide!
```

Obs.: os valores dependem dos vetores de teste no firmware.

Você pode gerar um log formatado para anexar no relatório com:

```bash
python3 execution_log.py
```

## Troubleshooting

- Ferramentas FPGA ausentes (yosys/nextpnr/prjtrellis):
	- Sintomas: erro ao iniciar síntese/place&route; mensagens indicando executáveis não encontrados.
	- Ação: instale a toolchain ECP5 open-source conforme links em "Requisitos/Dependências". Verifique se `yosys`, `nextpnr-ecp5` e `ecppack` (prjtrellis) estão no PATH.

- Erro de BIOS/timer0 ao compilar software no LiteX:
	- Sintomas: mensagens como "BIOS needs timer0 peripheral" durante a fase de software.
	- Ação: neste projeto, o build de gateware está configurado com `compile_software=False` para evitar essa dependência. Caso deseje compilar BIOS/software, garanta `with_timer=True` no SoC e um ambiente completo de software do LiteX.

- Carregar bitstream (`--load`/`--prog-only`) falha:
	- Sintomas: erro informando que `openFPGALoader`/`ecpprog` não está no PATH, ou bitstream não encontrado.
	- Ação: instale uma das ferramentas e garanta que está no PATH. Use `--loader ecpprog` para alternar, e `--bitstream <caminho>` para escolher o arquivo explicitamente.

- Revisão/board incorretos (Colorlight i5/i9):
	- Sintomas: falhas de pinos/constraints ou erros de plataforma.
	- Ação: especifique corretamente `--board` e `--revision` (ex.: `--board i9 --revision 7.2`). O padrão é i5 rev 7.0.

- Cabeçalhos `csr.h` não encontrados ao compilar o firmware:
	- Sintomas: erro no Makefile de `ip/` avisando que os headers não existem.
	- Ação: rode `make headers-only` ou `make build-soc` antes de `make -C ip`. Verifique se `build/dotp/software/include/generated/csr.h` foi gerado.

- Toolchain RISC-V:
	- Sintomas: `riscv32-unknown-elf-gcc` não encontrado.
	- Ação: instale uma toolchain RISC-V ou use a fornecida localmente (ajuste `CROSS_COMPILE`). Há um toolchain de exemplo em `tools/bin/` com wrappers; você pode compilar com `make -C ip CROSS_COMPILE=../tools/bin/riscv32-unknown-elf-`.


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
