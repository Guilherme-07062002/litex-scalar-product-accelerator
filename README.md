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

Ou então para baixar por linha de comando:

```sh
# Acesse o diretório tools
cd tools

# Baixe a versão mais recente do oss-cad-suite (verifique a página de releases para a versão mais atual)
wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2025-10-08/oss-cad-suite-linux-x64-20251008.tgz

# Ainda na mesma pasta, extraia o conteúdo do arquivo baixado
tar -xvzf oss-cad-suite-linux-x64-20251008.tgz
```

O `Makefile` na raiz do projeto automatiza o processo de simulação e testbench do acelerador. Para compilar e testar o projeto completo, siga os passos abaixo:

### 1. Simular o Acelerador (RTL)

Caso queira simular o acelerador e obter uma comparação entre a execução em hardware e software, execute:

```bash
make sim
```

Para executar o testbench apenas do acelerador, execute:

```bash
make tb
```

### 2. Acionar o ambiente do OSS CAD SUITE e Gere o SoC com LiteX
```sh
# Acionar o ambiente do OSS CAD SUITE
source tools/oss-cad-suite/oss-cad-suite/environment

# Busque o caminho do python3
which python3

# Gerar o SoC
caminho_do_python3 ./ip/colorlight_i5.py --board i9 --revision 7.2 --build --cpu-type=picorv32  --ecppack-compress
```

Se surgir alguma mensagem do tipo "No module named ...", faça a instalação do módulo faltante no ambiente virtual Python rodando:

```sh
pip3 install nome_do_modulo
```

E continue repetindo o processo até que não haja mais erros do tipo.

(Se assegure de estar baixando essas dependências no ambiente virtual Python, e não no sistema global.)

Caso essas dependências já estejam instaladas no sistema global, pode acontecer de o ambiente virtual não conseguir encontrá-las. Nesse caso, você pode tentar instalar as dependências diretamente no ambiente virtual com o comando acima.

### 3. Compilar o firmware
```sh
# Assumindo que você já está no diretório /ip
cd ./ip

# Compile o firmware
make
```

Se houver algum erro, tente executar o comando:

```sh
# Limpa arquivos de build anteriores
make clean
```

E tente novamente.

### 4. Gravar o bitstream e o firmware na placa
Primeiro, execute no terminal o seguinte comando:

```sh
which openFPGALoader
```

Copie o caminho descoberto e execute os próximos passos, colocando o caminho no local indicado. O openFPGALoader é uma ferramenta utilizada para carregar arquivos para o FPGA, e já vem por padrão no OSS CAD Suite.

```sh
# Assumindo que você já está no diretório ip
cd ip

# Grave o bitstream na placa
/caminho/descoberto -b colorlight-i5 build/colorlight_i5/gateware/colorlight_i5.bit
```

### 5. Executar via terminal serial na placa FPGA

Execute o seguinte comando:

```sh
# Abra o terminal serial (verifique a porta correta, pode ser ttyACM0 ou ttyACM1)
litex_term /dev/ttyACM0 --kernel ip/main.bin
```

Caso ocorra algum erro com relação a porta, tente mudar para "ttyACM1", ou verifique a porta utilizada no momento em que foi colocado o FPGA no dispositivo.

Após executar o comando acima aperte "enter" e digite "reboot". Automaticamente o FPGA será reiniciado e o programa será executado e mostrado no terminal.

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
