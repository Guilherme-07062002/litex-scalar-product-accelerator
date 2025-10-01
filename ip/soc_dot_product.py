#!/usr/bin/env python3

from migen import *
from litex.gen import *
from litex_boards.targets.colorlight_i5 import BaseSoC as ColorlightBaseSoC
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc_core import SoCCore

from dot_product_wrapper import DotProductAccel
import os
import glob
import shutil
import subprocess


class SoCWithDotProduct(ColorlightBaseSoC):
    def __init__(self, *args, **kwargs):
        # Permite desabilitar SPI flash apenas em cenários específicos (ex.: geração de headers)
        self._disable_spi_flash = kwargs.pop("disable_spi_flash", False)
        # Forçar uma CPU RISC-V padrão e UART
        kwargs.setdefault("cpu_type", "vexriscv")
        kwargs.setdefault("uart_name", "serial")
        kwargs.setdefault("integrated_rom_size", 0x8000)
        kwargs.setdefault("integrated_main_ram_size", 0x10000)
        # Habilita timer para compatibilidade com BIOS em builds completos
        kwargs.setdefault("with_timer", True)
        # Workaround: desabilitar LedChaser por bug de extração de nome de CSR na versão atual
        # do LiteX (CSRStorage sem nome explícito pode falhar em Python 3.12). Mantém-se os
        # demais periféricos padrão do target.
        kwargs.setdefault("with_led_chaser", False)

        super().__init__(*args, **kwargs)

        # Instancia e adiciona o acelerador
        self.dotp = DotProductAccel(self.platform, sys_clk_freq=int(kwargs.get("sys_clk_freq", 50e6)))
        # Adiciona CSR para o periférico
        self.add_csr("dotp")

    # Timer opcional: omitido aqui para facilitar geração de headers sem BIOS

    # Override controlado: desabilita SPI flash apenas quando solicitado
    def add_spi_flash(self, *args, **kwargs):
        if self._disable_spi_flash:
            # Ignora adição do SPI flash (workaround para bug de CSR em algumas versões)
            return
        # Caso contrário, delega para a implementação padrão do SoCCore
        return SoCCore.add_spi_flash(self, *args, **kwargs)


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(description="SoC Colorlight + Acelerador Produto Escalar")
    parser.add_target_argument("--board", default="i9")
    parser.add_target_argument("--revision", default="7.2")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float)
    parser.add_target_argument("--build", action="store_true")
    parser.add_target_argument("--load", action="store_true")
    parser.add_argument("--prog-only", action="store_true", help="Apenas carregar bitstream (sem build)")
    parser.add_argument("--loader", default="openFPGALoader", choices=["openFPGALoader", "ecpprog"], help="Ferramenta de gravação")
    parser.add_argument("--loader-board", default="colorlight", help="Board para openFPGALoader (ex.: colorlight)")
    parser.add_argument("--bitstream", default=None, help="Caminho para o bitstream (.bit/.svf); se omitido, detecta em build/dotp/gateware")
    # Gera apenas headers/CSRs e artefatos de software, sem sintetizar gateware
    parser.add_argument("--headers-only", action="store_true", help="Gerar apenas headers/CSRs (sem build de gateware)")
    args = parser.parse_args()

    def _detect_bitstream(default_gateware_dir: str) -> str:
        if args.bitstream:
            return args.bitstream
        # Procura por .bit, depois .svf
        candidates = []
        candidates += sorted(glob.glob(os.path.join(default_gateware_dir, "*.bit")))
        candidates += sorted(glob.glob(os.path.join(default_gateware_dir, "*.svf")))
        if candidates:
            return candidates[0]
        return None

    def _program_bitstream(bitstream_path: str) -> None:
        if not bitstream_path or not os.path.exists(bitstream_path):
            raise FileNotFoundError(f"Bitstream não encontrado: {bitstream_path}")
        if args.loader == "openFPGALoader":
            if not shutil.which("openFPGALoader"):
                raise RuntimeError("openFPGALoader não encontrado no PATH. Instale-o ou ajuste --loader.")
            cmd = ["openFPGALoader", "-b", args.loader_board, "-f", bitstream_path]
        elif args.loader == "ecpprog":
            if not shutil.which("ecpprog"):
                raise RuntimeError("ecpprog não encontrado no PATH. Instale-o ou ajuste --loader.")
            # -S carrega em SRAM
            cmd = ["ecpprog", "-S", bitstream_path]
        else:
            raise ValueError(f"Loader desconhecido: {args.loader}")
        print("INFO: Programando bitstream:", " ".join(cmd))
        subprocess.run(cmd, check=True)

    # Caminho padrão de saída do gateware
    default_gateware_dir = os.path.join("build", "dotp", "gateware")

    # Modo apenas programar
    if args.prog_only:
        bit = _detect_bitstream(default_gateware_dir)
        if not bit:
            raise FileNotFoundError(f"Nenhum bitstream encontrado em {default_gateware_dir}. Faça o build primeiro ou passe --bitstream.")
        _program_bitstream(bit)
        return

    soc = SoCWithDotProduct(
        board=args.board,
        revision=args.revision,
        sys_clk_freq=args.sys_clk_freq,
        # Workaround: ao gerar apenas headers, desabilitar SPI flash para evitar bug de CSR
        disable_spi_flash=args.headers_only,
        **parser.soc_argdict,
    )
    if args.headers_only:
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv",
                          compile_software=False, compile_gateware=False)
        # Finaliza o SoC e gera headers/CSRs diretamente, sem gateware/BIOS
        soc.finalize()
        builder._generate_includes(with_bios=False)
        builder._generate_csr_map()
        return
    else:
        # Evita compilar BIOS/software durante a síntese de gateware para não exigir timer0
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv", compile_software=False)
        builder.build(run=args.build)
        if args.load:
            bit = _detect_bitstream(builder.gateware_dir if hasattr(builder, "gateware_dir") else default_gateware_dir)
            if not bit:
                raise FileNotFoundError(f"Nenhum bitstream encontrado em {builder.gateware_dir if hasattr(builder, 'gateware_dir') else default_gateware_dir}. Verifique o build.")
            _program_bitstream(bit)

if __name__ == "__main__":
    main()
