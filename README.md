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
4.  **Firmware (`ip/main.c`)**: Aplicação bare-metal em C que roda na CPU RISC-V. Ele inicializa a comunicação serial, calcula o produto escalar em software, depois usa o acelerador de hardware e, por fim, compara os dois resultados, imprimindo o status no terminal.

## Como Compilar e Executar

É recomendado utilizar um ambiente virtual Python.

Baixe o oss-cad-suite de acordo com a release compatível com seu sistema operacional em:

[https://github.com/YosysHQ/oss-cad-suite-build/releases](https://github.com/YosysHQ/oss-cad-suite-build/releases)

Insira o arquivo compactado oss-cad-suite do baixado em `/tools` e realize a extração do conteúdo na mesma pasta.

O `Makefile` na raiz do projeto automatiza as principais tarefas.

#### 1. Simular o Acelerador (RTL)

Para verificar a lógica do acelerador de forma isolada:

```bash
make sim
```

Este comando executa o testbench (`tb/`) e gera um arquivo de ondas (`sim/dot_product_accel.vcd`) para análise.

#### 2. **Acione o ambiente do OSS CAD SUITE e Gere o SoC com LiteX**
```sh
# Acionar o ambiente do OSS CAD SUITE
source tools/oss-cad-suite/oss-cad-suite/environment

# Acessar o diretório com a implementação do SoC
cd ip/

# Busque o caminho do python3
which python3

# Gerar o SoC
caminho_do_python3 colorlight_i5.py --board i9 --revision 7.2 --build --cpu-type=picorv32  --ecppack-compress
```

Se surgir alguma mensagem do tipo "No module named ...", faça a instalação do módulo faltante no ambiente virtual Python rodando:

```sh
pip3 install nome_do_modulo
```

E continue repetindo o processo até que não haja mais erros do tipo.

#### 3. **Compile o firmware**
```sh
# Assumindo que você já está no diretório /ip
cd ../ip

# Compile o firmware
make
```

Se houver algum erro, tente executar o comando:

```sh
# Limpa arquivos de build anteriores
make clean
```

E tente novamente.

#### 4. **Grave o bitstream e o firmware na placa**
Primeiro, execute no terminal o seguinte comando:

```sh
which openFPGALoader
```

Copie o caminho descoberto e execute os próximos passos, colocando o caminho no local indicado. O openFPGALoader é uma ferramenta utilizada para carregar arquivos para o FPGA, e já vem por padrão no OSS CAD Suite.

```sh
# Assumindo que você já está no diretório /ip
cd /ip

# Grave o bitstream na placa
/caminho/descoberto -b colorlight-i5 build/colorlight_i5/gateware/colorlight_i5.bit
```

#### 5. **Execute e teste via terminal serial**
Execute o seguinte comando, e caso não apareça nada, aperte "enter".

```sh
# Abra o terminal serial (verifique a porta correta, pode ser ttyACM0 ou ttyACM1)
litex_term /dev/ttyACM0 --kernel ../firmware/main.bin
```

Caso ocorra algum erro com relação a porta, tente mudar para "ttyACM1", ou verifique a porta utilizada no momento em que foi colocado o FPGA no dispositivo.

Após abrir o terminal, aperte "enter" e digite "reboot". Automaticamente o FPGA será reiniciado, e o programa será executado e mostrado no terminal.

O Makefile procura os headers/bibliotecas gerados em `build/dotp/software/include/generated` e produz `ip/firmware.elf` e `ip/firmware.bin`.

Execução: conectar via UART (serial) ao SoC; o firmware imprime os resultados de SW e HW e a verificação `[OK]`.

### Log de Execução (exemplo esperado)

```text
LiteX Dot-Product Accelerator Demo
CPU: VexRiscv
Software: 0xFFFFFFFFFFFFFFF8
Hardware: 0xFFFFFFFFFFFFFFF8
[OK] Resultado coincide!
```

Obs.: os valores dependem dos vetores de teste no firmware. Para pontuar a seção de resultados, inclua um log UART real (texto ou asciinema) da execução do firmware.

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
