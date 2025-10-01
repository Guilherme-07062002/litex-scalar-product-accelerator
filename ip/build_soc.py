"""
Script auxiliar para invocar o build do SoC com o dot-product peripheral.

Uso (exemplo):
    python build_soc.py --board i9 --revision 7.2 --sys-clk-freq 60000000 --build

Observação: requer LiteX instalado no ambiente e ferramentas de síntese ECP5 para gerar bitstream.
"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Build SoC with dot-product peripheral (LiteX)")
    parser.add_argument('--build', action='store_true', help='Run liteX build')
    parser.add_argument('--board', default='i9', help='Target board (i5 ou i9)')
    parser.add_argument('--sys-clk-freq', type=int, default=60000000, help='System clock frequency')
    parser.add_argument('--cpu-type', default='vexriscv', help='CPU type')
    parser.add_argument('--revision', dest='revision', default='7.2', help='Board revision (ex.: 7.2)')
    args = parser.parse_args()

    # Import here to avoid hard dependency if user only wants other features
    try:
        from soc_dot_product import SoCWithDotProduct
    except Exception as e:
        print("Erro ao importar LiteX ou o módulo SoC. Verifique se o ambiente tem LiteX e litex-boards instalados.")
        raise

    soc = SoCWithDotProduct(board=args.board, revision=args.revision, cpu_type=args.cpu_type, sys_clk_freq=args.sys_clk_freq)

    if args.build:
        print("Iniciando build do SoC (LiteX). Isso pode demorar e requer toolchain/FPGA tools.")
        from litex.soc.integration.builder import Builder
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv", compile_software=False)
        builder.build()

if __name__ == '__main__':
    main()
