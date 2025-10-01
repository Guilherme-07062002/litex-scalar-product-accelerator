#!/usr/bin/env python3

from migen import *
from litex.gen import *
from litex_boards.targets.colorlight_i5 import BaseSoC as ColorlightBaseSoC
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc_core import SoCCore

from dot_product_wrapper import DotProductAccel


class SoCWithDotProduct(ColorlightBaseSoC):
    def __init__(self, *args, **kwargs):
        # Forçar uma CPU RISC-V padrão e UART
        kwargs.setdefault("cpu_type", "vexriscv")
        kwargs.setdefault("uart_name", "serial")
        kwargs.setdefault("integrated_rom_size", 0x8000)
        kwargs.setdefault("integrated_main_ram_size", 0x10000)
        # Evite dependências desnecessárias no BIOS durante geração de headers
        kwargs.setdefault("with_timer", False)
        # Disable LED chaser by default to avoid CSR name-extraction issues in some environments
        kwargs.setdefault("with_led_chaser", False)
        # Disable SPI Flash to avoid CSR naming issues
        kwargs.setdefault("integrated_rom_init", [])
        kwargs.setdefault("with_spi_flash", False)

        super().__init__(*args, **kwargs)

    def add_spi_flash(self, *args, **kwargs):
        # Override to disable SPI flash
        pass

        # Instancia e adiciona o acelerador
        self.dotp = DotProductAccel(self.platform, sys_clk_freq=int(kwargs.get("sys_clk_freq", 60e6)))
        # Adiciona CSR para o periférico
        self.add_csr("dotp")

    # Timer opcional: omitido aqui para facilitar geração de headers sem BIOS


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(description="SoC Colorlight + Acelerador Produto Escalar")
    parser.add_target_argument("--board", default="i5")
    parser.add_target_argument("--revision", default="7.0")
    parser.add_target_argument("--sys-clk-freq", default=60e6, type=float)
    parser.add_target_argument("--build", action="store_true")
    parser.add_target_argument("--load", action="store_true")
    # Gera apenas headers/CSRs e artefatos de software, sem sintetizar gateware
    parser.add_argument("--headers-only", action="store_true", help="Gerar apenas headers/CSRs (sem build de gateware)")
    args = parser.parse_args()

    soc = SoCWithDotProduct(board=args.board, revision=args.revision, sys_clk_freq=args.sys_clk_freq, **parser.soc_argdict)
    if args.headers_only:
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv",
                          compile_software=False, compile_gateware=False)
        # Finaliza o SoC e gera headers/CSRs diretamente, sem gateware/BIOS
        soc.finalize()
        builder._generate_includes(with_bios=False)
        builder._generate_csr_map()
        return
    else:
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv")
        builder.build(run=args.build, load=args.load)

if __name__ == "__main__":
    main()
