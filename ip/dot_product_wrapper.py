# dot_product_wrapper.py
# Wrapper LiteX/Migen para o módulo SystemVerilog dot_product_accel

from migen import *
from litex.gen import LiteXModule
from litex.soc.interconnect.csr import CSRStorage, CSRStatus


class DotProductAccel(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        # 16 registradores de entrada (a0..a7, b0..b7), cada um 32-bit
        self.a = [CSRStorage(32, name=f"a{i}") for i in range(8)]
        self.b = [CSRStorage(32, name=f"b{i}") for i in range(8)]

        # start (1 bit)
        self.start = CSRStorage(1, name="start")

        # done (1 bit) e result (64 bits)
        self.done      = CSRStatus(1, name="done")
        self.result_lo = CSRStatus(32, name="result_lo")
        self.result_hi = CSRStatus(32, name="result_hi")

        # Sinais internos
        a_sigs = [Signal(32, name=f"a{i}") for i in range(8)]
        b_sigs = [Signal(32, name=f"b{i}") for i in range(8)]
        start  = Signal()
        done   = Signal()
        result = Signal(64)

        # Atribuições CSR -> sinais
        for i in range(8):
            self.comb += a_sigs[i].eq(self.a[i].storage)
            self.comb += b_sigs[i].eq(self.b[i].storage)
        self.comb += start.eq(self.start.storage)

        # Exporta done/result para CSRs de leitura
        self.sync += [
            self.done.status.eq(done),
            self.result_lo.status.eq(result[:32]),
            self.result_hi.status.eq(result[32:]),
        ]

        # Clock/Reset
        clk   = ClockSignal()
        rst   = ResetSignal()

        # Inclui o arquivo SystemVerilog ao projeto
        platform.add_source("rtl/dot_product_accel.sv")

        # Instancia o módulo SV
        self.specials += Instance("dot_product_accel",
            i_clk=clk,
            i_rst=rst,
            i_start=start,
            o_done=done,
            i_a0=a_sigs[0], i_a1=a_sigs[1], i_a2=a_sigs[2], i_a3=a_sigs[3],
            i_a4=a_sigs[4], i_a5=a_sigs[5], i_a6=a_sigs[6], i_a7=a_sigs[7],
            i_b0=b_sigs[0], i_b1=b_sigs[1], i_b2=b_sigs[2], i_b3=b_sigs[3],
            i_b4=b_sigs[4], i_b5=b_sigs[5], i_b6=b_sigs[6], i_b7=b_sigs[7],
            o_result=result,
        )
