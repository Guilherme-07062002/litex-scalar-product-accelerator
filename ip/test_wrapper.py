#!/usr/bin/env python3

"""
Script para testar apenas a geração de CSRs do nosso wrapper
"""

from migen import *
from litex.gen import *
from litex.soc.interconnect.csr import *
from litex.build.lattice import LatticePlatform
from litex.build.generic_platform import *

from dot_product_wrapper import DotProductAccel

# Platform mínima
_io = [
    ("clk25", 0, Pins("P3"), IOStandard("LVCMOS33")),
]

class TestPlatform(LatticePlatform):
    def __init__(self):
        LatticePlatform.__init__(self, "LFE5U-25F-6BG381C", _io, toolchain="trellis")

def test_wrapper():
    """Testa se o wrapper pode ser instanciado e se os CSRs são criados"""
    
    platform = TestPlatform()
    
    print("Criando wrapper DotProductAccel...")
    wrapper = DotProductAccel(platform, 50e6)
    
    print("✅ Wrapper criado com sucesso!")
    
    print("\n📋 CSRs de entrada (32-bit cada):")
    for i in range(8):
        csr_a = getattr(wrapper, f'a{i}')
        csr_b = getattr(wrapper, f'b{i}')
        print(f"  a{i}: {csr_a}")
        print(f"  b{i}: {csr_b}")
    
    print(f"\n🚦 CSR de controle:")
    print(f"  start: {wrapper.start}")
    
    print(f"\n📤 CSRs de saída:")
    print(f"  done: {wrapper.done}")
    print(f"  result_lo: {wrapper.result_lo}")
    print(f"  result_hi: {wrapper.result_hi}")
    
    # Simula o CSR map
    csr_map = {}
    offset = 0
    
    for i in range(8):
        csr_map[f'dotp_a{i}'] = offset
        offset += 1
        csr_map[f'dotp_b{i}'] = offset  
        offset += 1
    
    csr_map['dotp_start'] = offset
    offset += 1
    csr_map['dotp_done'] = offset
    offset += 1
    csr_map['dotp_result_lo'] = offset
    offset += 1
    csr_map['dotp_result_hi'] = offset
    
    print(f"\n🗺️  Mapa CSR estimado:")
    for name, addr in csr_map.items():
        print(f"  {name}: 0x{addr:04x}")
    
    print(f"\n✅ Total de CSRs: {len(csr_map)}")

if __name__ == "__main__":
    test_wrapper()