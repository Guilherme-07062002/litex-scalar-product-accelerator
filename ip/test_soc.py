#!/usr/bin/env python3

"""
SoC mínimo para testar apenas o acelerador de produto escalar
"""

from migen import *
from litex.gen import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.clock import *
from litex.build.lattice import LatticePlatform
from litex.build.generic_platform import *

from dot_product_wrapper import DotProductAccel

# CRG simples
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        clk25 = platform.request("clk25")
        self.comb += self.cd_sys.clk.eq(clk25)

# Platform mínima para teste
_io = [
    ("clk25", 0, Pins("P3"), IOStandard("LVCMOS33")),
    ("serial", 0,
        Subsignal("tx", Pins("P4")),
        Subsignal("rx", Pins("P5")),
        IOStandard("LVCMOS33")
    ),
]

class TestPlatform(LatticePlatform):
    default_clk_name = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self):
        LatticePlatform.__init__(self, "LFE5U-25F-6BG381C", _io, toolchain="trellis")

class TestSoC(SoCCore):
    def __init__(self, **kwargs):
        platform = TestPlatform()
        
        # SoC mínimo
        SoCCore.__init__(self, platform, 50e6,
            ident="Test SoC with DotProduct",
            with_uart=True,
            uart_name="serial",
            integrated_rom_size=0x8000,
            integrated_main_ram_size=0x10000,
            **kwargs
        )

        # Clock/Reset básicos
        self.submodules.crg = _CRG(platform)

        # Adiciona nosso acelerador
        self.submodules.dotp = DotProductAccel(platform, 50e6)
        self.add_csr("dotp")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test SoC para gerar headers CSR")
    parser.add_argument("--headers-only", action="store_true", help="Gerar apenas headers CSR")
    args = parser.parse_args()

    soc = TestSoC()
    
    if args.headers_only:
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv",
                          compile_software=False, compile_gateware=False)
        soc.finalize()
        builder._generate_includes(with_bios=False)
        builder._generate_csr_map()
        print("Headers CSR gerados em build/dotp/")
        return
    else:
        builder = Builder(soc, output_dir="build/dotp", csr_csv="build/dotp/csr.csv")
        builder.build()

if __name__ == "__main__":
    main()