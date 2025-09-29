// firmware_dotp.c - Firmware para interagir com o acelerador de produto escalar via CSR
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Os headers csr.h e system.h serão gerados pelo LiteX durante o build.
#include <generated/csr.h>
#include <generated/soc.h>

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
    dotp_start_write(1);
}

static bool hw_done() {
    return dotp_done_done_read();
}

static int64_t hw_result() {
    uint32_t lo = dotp_result_lo_read();
    uint32_t hi = dotp_result_hi_read();
    return ((int64_t)(int32_t)hi << 32) | lo;
}

int main(void) {
    printf("\nLiteX Dot-Product Accelerator Demo\n");
    printf("CPU: %s\n", CPU_DESCRIPTION);

    // Vetores de teste
    int32_t A[8] = {1, -2, 3, -4, 5, -6, 7, -8};
    int32_t B[8] = {8, 7, -6, -5, 4, 3, -2, -1};

    // Software
    int64_t sw = sw_dotp(A, B);
    printf("Software: %lld\n", (long long)sw);

    // Hardware
    hw_write_vectors(A, B);
    hw_start();
    while (!hw_done());
    int64_t hw = hw_result();
    printf("Hardware: %lld\n", (long long)hw);

    if (hw == sw) {
        printf("[OK] Resultado coincide!\n");
    } else {
        printf("[ERRO] Resultado diferente!\n");
    }

    // Loop simples para observar via UART
    while (1) {
        // Nada, poderia aguardar comandos via UART futuramente
    }
    return 0;
}
