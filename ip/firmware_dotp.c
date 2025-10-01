// firmware_dotp.c - Firmware bare-metal para interagir com o acelerador de produto escalar via CSR
#include <stdint.h>
#include <stdbool.h>

// Headers gerados pelo LiteX durante o build (--headers-only já gera estes arquivos)
#include <csr.h>
#include <soc.h>

// UART mínimo (usa o periférico UART do LiteX)
#ifndef CSR_UART_BASE
__attribute__((weak)) int uart_txfull_read(void) { return 0; }
__attribute__((weak)) void uart_rxtx_write(uint8_t c) { (void)c; }
#endif
static inline void uart_write_char(char c) {
    // Aguarda espaço no TX
    while (uart_txfull_read());
    uart_rxtx_write((uint8_t)c);
}

static void uart_write_str(const char* s) {
    while (*s) {
        if (*s == '\n') uart_write_char('\r');
        uart_write_char(*s++);
    }
}

static void uart_write_hex32(uint32_t v) {
    static const char* hex = "0123456789ABCDEF";
    uart_write_str("0x");
    for (int i = 7; i >= 0; --i) {
        uart_write_char(hex[(v >> (i*4)) & 0xF]);
    }
}

static void uart_write_hex64(uint64_t v) {
    uint32_t hi = (uint32_t)(v >> 32);
    uint32_t lo = (uint32_t)(v & 0xFFFFFFFFu);
    uart_write_str("0x");
    static const char* hex = "0123456789ABCDEF";
    for (int i = 7; i >= 0; --i) uart_write_char(hex[(hi >> (i*4)) & 0xF]);
    for (int i = 7; i >= 0; --i) uart_write_char(hex[(lo >> (i*4)) & 0xF]);
}

static int64_t sw_dotp(const int32_t a[8], const int32_t b[8]) {
    int64_t acc = 0;
    for (int i=0;i<8;i++) acc += (int64_t)a[i]*(int64_t)b[i];
    return acc;
}

static void hw_write_vectors(const int32_t a[8], const int32_t b[8]) {
    dotp_a0_write(a[0]); dotp_a1_write(a[1]); dotp_a2_write(a[2]); dotp_a3_write(a[3]);
    dotp_a4_write(a[4]); dotp_a5_write(a[5]); dotp_a6_write(a[6]); dotp_a7_write(a[7]);
    dotp_b0_write(b[0]); dotp_b1_write(b[1]); dotp_b2_write(b[2]); dotp_b3_write(b[3]);
    dotp_b4_write(b[4]); dotp_b5_write(b[5]); dotp_b6_write(b[6]); dotp_b7_write(b[7]);
}

static void hw_start() {
    // Gera um pulso em 'start' para evitar reexecuções involuntárias
    // Caso o bit fique em nível alto até o DONE, o hardware poderia reiniciar
    // automaticamente uma nova operação. Portanto, pulse e depois limpe.
    dotp_start_write(1);
    // Pequeno atraso para garantir pelo menos 1-2 ciclos de clock do SoC
    for (volatile int i = 0; i < 16; ++i) { /* noop */ }
    dotp_start_write(0);
}

static bool hw_done() {
    return dotp_done_read();
}

static int64_t hw_result() {
    uint32_t lo = dotp_result_lo_read();
    uint32_t hi = dotp_result_hi_read();
    return ((int64_t)(int32_t)hi << 32) | lo;
}

int main(void) {
    uart_write_str("\nLiteX Dot-Product Accelerator Demo\n");
    uart_write_str("CPU: "); uart_write_str(CPU_DESCRIPTION); uart_write_str("\n");

    // Vetores de teste
    int32_t A[8] = {1, -2, 3, -4, 5, -6, 7, -8};
    int32_t B[8] = {8, 7, -6, -5, 4, 3, -2, -1};

    // Software
    int64_t sw = sw_dotp(A, B);
    uart_write_str("Software: "); uart_write_hex64((uint64_t)sw); uart_write_str("\n");

    // Hardware
    hw_write_vectors(A, B);
    hw_start();
    while (!hw_done());
    int64_t hw = hw_result();
    uart_write_str("Hardware: "); uart_write_hex64((uint64_t)hw); uart_write_str("\n");

    if (hw == sw) uart_write_str("[OK] Resultado coincide!\n");
    else           uart_write_str("[ERRO] Resultado diferente!\n");

    // Loop simples para observar via UART
    while (1) {
        // Nada, poderia aguardar comandos via UART futuramente
    }
    return 0;
}
