# Tarefa 04 — SoC com LiteX: Acelerador de Produto Escalar via CSR

Este repositório reaproveita a estrutura da tarefa anterior (testes em SV) e adiciona:

- Acelerador de produto escalar 8×32 bits (signed) com resultado 64 bits.
- Wrapper LiteX com interface via CSR (a0..a7, b0..b7, start, done, result_lo/hi).
- Integração ao target Colorlight i5 (i9v7.2 compatível) usando LiteX.
- Firmware em C para envio de dados, acionamento do acelerador e comparação com software.

## Objetivo

Demonstrar a integração de um bloco SV customizado como periférico CSR em um SoC LiteX e compará-lo com a implementação em software via UART.

## Estrutura

```text
rtl/            Módulos RTL (registradores, contador, ULA, multiplicador)
tb/             Testbench
sim/            Saída de simulação (VVP, VCD)
build/          Script de automação (menu)
doc/            (espaço para relatório/diagramas)
ip/             Wrapper LiteX, SoC Python e firmware C
```

## Módulos (tarefa anterior)

`shift_register.sv` registrador universal (hold, shift L/R, carga paralela, ser_in/ser_out).

`counter.sv` contador com load+enable (modo decremento aqui). Saturação em zero. Sinais: data_out, end_flag.

`ula_74181.sv` / `ula_8_bits.sv` ULA em dois estágios (só soma usada).

`shift_add_multiplier.sv` integra A, B, Q, contador e ULA com FSM.

`tb_shift_add_multiplier.sv` vetores de teste e geração de VCD.

## Novo módulo (tarefa 04)

`dot_product_accel.sv` Acelerador de produto escalar 8×32 (signed) → 64 bits, interface com `start/done` e inputs `a0..a7`, `b0..b7`. Implementação sequencial (8 ciclos) e testbench `tb_dot_product_accel.sv` com checagem automática.

## Execução (menu SV)

No Bash:

```bash
bash build/build.sh
```

Menu principal traz opções para ULAs, multiplicador e abrir ondas.

- Opção 3 → 1 roda o testbench do multiplicador. VCD: `sim/shift_add_multiplier.vcd`.
- Opção 4 → 1 roda o testbench do produto escalar. VCD: `sim/dot_product_accel.vcd`.

## Execução Direta (exemplos)

Multiplicador:

```bash
iverilog -g2012 -o sim/shift_add_multiplier.vvp \
    rtl/ula_74181.sv rtl/ula_8_bits.sv rtl/shift_register.sv rtl/counter.sv rtl/shift_add_multiplier.sv \
    tb/tb_shift_add_multiplier.sv && vvp sim/shift_add_multiplier.vvp
```

Produto escalar:

```bash
iverilog -g2012 -o sim/dot_product_accel.vvp rtl/dot_product_accel.sv tb/tb_dot_product_accel.sv && vvp sim/dot_product_accel.vvp
```

Abrir ondas (se GTKWave instalado):

```bash
gtkwave sim/shift_add_multiplier.vcd &
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

- https://github.com/enjoy-digital/litex
- https://github.com/litex-hub/litex-boards

### Build do SoC

Gera bitstream e headers para firmware. Exemplo para i5 rev 7.2:

```bash
python -m ip.soc_dot_product --board i5 --revision 7.2 --sys-clk-freq 60000000 --build
```

Saídas relevantes:

- `build/dotp/csr.csv` e `build/dotp/software/include/generated/csr.h`
- Bitstream em `build/dotp/gateware/`

Para carregar (quando suportado no ambiente):

```bash
python -m ip.soc_dot_product --board i5 --revision 7.2 --load
```

### Compilar/rodar firmware

Após o build do SoC, entre em `build/dotp/software` e compile com o ambiente LiteX (o Builder já estrutura o projeto e compila o BIOS/firmware quando configurado). Opcionalmente, você pode criar um `Makefile` próprio apontando para os headers em `include/generated/`.

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
