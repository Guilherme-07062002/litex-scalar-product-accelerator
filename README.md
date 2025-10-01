# Acelerador de Produto Escalar com LiteX e CSR

Este projeto demonstra a criação de um System-on-Chip (SoC) na FPGA Colorlight i5, utilizando o framework LiteX. O SoC integra um processador RISC-V com um acelerador de hardware customizado para cálculo de produto escalar, com o qual o processador se comunica através de um barramento CSR (Control and Status Register).

O objetivo é apresentar um caso de uso completo, desde o design do acelerador em SystemVerilog, sua integração ao SoC via Python/Migen, até o desenvolvimento de um firmware em C para validar a operação e comparar o desempenho com uma implementação puramente em software.

## Arquitetura do Projeto

O projeto está organizado nos seguintes diretórios principais:

-   `rtl/`: Contém o código-fonte do acelerador de produto escalar em SystemVerilog.
-   `tb/`: Inclui o testbench para a verificação funcional do acelerador.
-   `ip/`: Contém os arquivos de integração com o LiteX (`wrapper`, `SoC`) e o firmware (`.c`, `.ld`).
-   `tools/`: Scripts e toolchains auxiliares para o processo de build.

### Componentes Principais

1.  **Acelerador (`rtl/dot_product_accel.sv`)**: Módulo em SystemVerilog que calcula o produto escalar entre dois vetores de 8 elementos (32-bit signed). A operação leva 8 ciclos de clock e o resultado é um valor de 64 bits.
2.  **Wrapper LiteX (`ip/dot_product_wrapper.py`)**: Uma classe Python que "envolve" o módulo SystemVerilog, expondo suas portas de entrada e saída como registradores no barramento CSR. É a ponte entre o hardware customizado e o ecossistema LiteX.
3.  **SoC (`ip/soc_dot_product.py`)**: Script principal que define o SoC, baseado no target `colorlight_i5` do LiteX. Ele instancia a CPU, a memória e mantém os periféricos padrão do target (ex.: LED chaser, SPI flash), adicionando o acelerador de produto escalar como um novo periférico.
4.  **Firmware (`ip/firmware_dotp.c`)**: Aplicação bare-metal em C que roda na CPU RISC-V. Ele inicializa a comunicação serial, calcula o produto escalar em software, depois usa o acelerador de hardware e, por fim, compara os dois resultados, imprimindo o status no terminal.

## Como Compilar e Executar

É recomendado utilizar um ambiente virtual Python.

```bash
# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install litex litex-boards
```

O `Makefile` na raiz do projeto automatiza as principais tarefas.

#### 1. Simular o Acelerador (RTL)

Para verificar a lógica do acelerador de forma isolada:

```bash
make sim
```

Este comando executa o testbench (`tb/`) e gera um arquivo de ondas (`sim/dot_product_accel.vcd`) para análise.

#### 2. Gerar Headers e Compilar o Firmware

Antes de compilar o firmware, é preciso gerar os headers C com o mapa de registradores do SoC:

```bash
# Gera build/dotp/software/include/generated/csr.h
make headers-only
```

Com os headers gerados, compile o firmware:

```bash
# Usa a toolchain em tools/bin para compilar o firmware
make -C ip CROSS_COMPILE=../tools/bin/riscv32-unknown-elf- all
```

#### 3. Simular o Firmware (End-to-End)

É possível simular a execução do firmware no SoC sem precisar de uma FPGA. Este teste valida a comunicação entre a CPU e o acelerador:

```bash
.venv/bin/python ip/firmware_sim.py
```

#### 4. Construir o SoC e Carregar na FPGA (Opcional)

Se você tiver a toolchain de FPGA para a ECP5 instalada (Yosys, nextpnr, prjtrellis), pode sintetizar o projeto:

```bash
# Constrói o gateware (.bit)
make build-soc
```

Para carregar o bitstream na Colorlight i5 (requer `openFPGALoader`):

```bash
# Carrega o bitstream na SRAM da FPGA
make load
```

## Mapa de CSR do Acelerador

A comunicação entre a CPU e o acelerador `dotp` é feita pelos seguintes registradores, mapeados em memória. O endereço base do periférico é `0xf0000000`.

| Registrador      | Endereço (Offset) | Acesso | Descrição                               |
| ---------------- | ----------------- | ------ | ----------------------------------------- |
| `dotp_a0`        | `0x00`            | RW     | Elemento 0 do vetor A (32 bits)           |
| ...              | ...               | ...    | ...                                       |
| `dotp_a7`        | `0x1C`            | RW     | Elemento 7 do vetor A (32 bits)           |
| `dotp_b0`        | `0x20`            | RW     | Elemento 0 do vetor B (32 bits)           |
| ...              | ...               | ...    | ...                                       |
| `dotp_b7`        | `0x3C`            | RW     | Elemento 7 do vetor B (32 bits)           |
| `dotp_start`     | `0x40`            | RW     | Inicia o cálculo (escrita de 1)           |
| `dotp_done`      | `0x44`            | RO     | Status; 1 quando o cálculo está pronto    |
| `dotp_result_lo` | `0x48`            | RO     | 32 bits inferiores do resultado (64 bits) |
| `dotp_result_hi` | `0x4C`            | RO     | 32 bits superiores do resultado (64 bits) |

## Log de Execução

Há dois modos de obter o log:

1) Simulação (rápido): usando `ip/firmware_sim.py`, que emula os CSRs e imprime o mesmo fluxo do firmware real.

```text
LiteX Dot-Product Accelerator Demo
CPU: VexRiscv
Software: 0xFFFFFFFFFFFFFFF8
Hardware: 0xFFFFFFFFFFFFFFF8
[OK] Resultado coincide!
```

2) UART real (recomendado para entrega): conecte-se via serial à placa para capturar a saída do firmware.

Exemplo com picocom (Linux):

```bash
picocom -b 115200 /dev/ttyUSB0 --imap lfcrlf
```

Exemplo com minicom (Linux):

```bash
minicom -b 115200 -D /dev/ttyUSB0
```

Depois de carregar o bitstream e rodar o firmware, copie o texto exibido no terminal e salve como `docs/uart_log.txt` (ou faça um cast no asciinema e inclua o link no README).

## Referências

-   [LiteX](https://github.com/enjoy-digital/litex)
-   [LiteX Boards](https://github.com/litex-hub/litex-boards)
-   [Building a SoC with LiteX](https://www.controlpaths.com/2022/01/17/building-soc-litex/)
-   [FPGA 101 Workshop](https://github.com/litex-hub/fpga_101)

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

### Mapa de CSR

O mapa de registradores do acelerador `dotp` é gerado dinamicamente pelo LiteX. Abaixo está um exemplo do mapa gerado para este projeto, que pode ser encontrado em `build/dotp/csr.csv`.

| Registrador      | Endereço (Offset) | Acesso | Descrição                               |
| ---------------- | ----------------- | ------ | ----------------------------------------- |
| `dotp_a0`        | `0x00`            | RW     | Elemento 0 do vetor A (32 bits)           |
| `dotp_a1`        | `0x04`            | RW     | Elemento 1 do vetor A (32 bits)           |
| ...              | ...               | ...    | ...                                       |
| `dotp_a7`        | `0x1C`            | RW     | Elemento 7 do vetor A (32 bits)           |
| `dotp_b0`        | `0x20`            | RW     | Elemento 0 do vetor B (32 bits)           |
| ...              | ...               | ...    | ...                                       |
| `dotp_b7`        | `0x3C`            | RW     | Elemento 7 do vetor B (32 bits)           |
| `dotp_start`     | `0x40`            | RW     | Inicia o cálculo (escrita de 1)           |
| `dotp_done`      | `0x44`            | RO     | Status; 1 quando o cálculo está pronto    |
| `dotp_result_lo` | `0x48`            | RO     | 32 bits inferiores do resultado (64 bits) |
| `dotp_result_hi` | `0x4C`            | RO     | 32 bits superiores do resultado (64 bits) |

O endereço base do periférico (`csr_base`) é `0xf0000000`.

### Log de Execução

Abaixo, o log de saída esperado no terminal serial ao executar o firmware na placa ou através da simulação (`ip/firmware_sim.py`).

```text
LiteX Dot-Product Accelerator Demo
CPU: VexRiscv
Software: 0xFFFFFFFFFFFFFFF8
Hardware: 0xFFFFFFFFFFFFFFF8
[OK] Resultado coincide!
```

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

Nota: Para cumprir o requisito "mantendo os periféricos já configurados", este SoC mantém o LED chaser e SPI flash do target. Caso seu ambiente não possua SPI flash conectado, o SoC continuará funcional; apenas ignore funcionalidades relacionadas ao flash.

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
