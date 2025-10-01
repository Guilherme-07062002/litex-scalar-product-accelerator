"""
Script auxiliar para invocar o build do SoC com o dot-product peripheral.

Uso (exemplo):
  python build_soc.py --board i5 --sys-clk-freq 60000000 --build

Observação: requer LiteX instalado no ambiente e ferramentas de síntese ECP5 para gerar bitstream.
"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Build SoC with dot-product peripheral (LiteX)")
    parser.add_argument('--build', action='store_true', help='Run liteX build')
    parser.add_argument('--board', default='i5', help='Target board (default: i5)')
    parser.add_argument('--sys-clk-freq', type=int, default=60000000, help='System clock frequency')
    parser.add_argument('--cpu-type', default='vexriscv', help='CPU type')
    parser.add_argument('--rev', default=None, help='Board revision (e.g., 7.2)')
    args = parser.parse_args()

    # Import here to avoid hard dependency if user only wants other features
    try:
        from soc_dot_product import SoCWithDotProduct
    except Exception as e:
        print("Erro ao importar LiteX ou o módulo SoC. Verifique se o ambiente tem LiteX e litex-boards instalados.")
        raise

    soc = SoCWithDotProduct(cpu_type=args.cpu_type, sys_clk_freq=args.sys_clk_freq)

    if args.build:
        print("Iniciando build do SoC (LiteX). Isso pode demorar e requer toolchain/FPGA tools.")
        from litex.soc.integration.builder import Builder
        builder = Builder(soc, csr_csv="build/dotp/csr.csv")
        builder.build()

if __name__ == '__main__':
    main()
