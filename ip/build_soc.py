"""
Script auxiliar para invocar o build do SoC com o periférico de produto escalar.

Uso (exemplos):
  python ip/build_soc.py --board i9 --revision 7.2 --sys-clk-freq 60000000 --build
  python ip/build_soc.py --board i9 --revision 7.2 --load

Observação: requer LiteX instalado no ambiente e ferramentas de síntese ECP5 para gerar bitstream.
"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Build SoC with dot-product peripheral (LiteX)")
    parser.add_argument('--build', action='store_true', help='Run LiteX build')
    parser.add_argument('--load',  action='store_true', help='Load bitstream/firmware if supported')
    parser.add_argument('--board', default='i5', help='Target board (i5 or i9)')
    parser.add_argument('--revision', default='7.2', help='Board revision (e.g., 7.2)')
    parser.add_argument('--sys-clk-freq', type=float, default=60e6, help='System clock frequency')
    parser.add_argument('--cpu-type', default='vexriscv', help='CPU type (default: vexriscv)')
    args = parser.parse_args()

    # Import aqui para evitar hard dependency se o usuário só quiser ler ajuda
    try:
        from ip.soc_dot_product import SoCWithDotProduct
        from litex.soc.integration.builder import Builder
    except Exception as e:
        print("Erro ao importar LiteX ou módulo SoC. Verifique se o ambiente tem LiteX instalado.")
        print(e)
        sys.exit(1)

    # Instancia SoC com parâmetros passados
    soc = SoCWithDotProduct(board=args.board, revision=args.revision, sys_clk_freq=args.sys_clk_freq, cpu_type=args.cpu_type)

    # Builder com diretório e csv definidos
    builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv")
    # Executa build/load conforme flags
    builder.build(run=args.build, load=args.load)

if __name__ == '__main__':
    main()
