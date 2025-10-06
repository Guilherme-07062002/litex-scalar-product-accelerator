// firmware_dotp.c - Firmware para interagir com o acelerador de produto escalar via CSR
#if defined(__has_include)
  #if __has_include(<stdio.h>)
    #include <stdio.h>
  #else
    /* Minimal declarations to satisfy IntelliSense or builds without system headers */
    int printf(const char *format, ...);
    int puts(const char *s);
    int putchar(int c);
  #endif
#else
  /* Fallback when __has_include is not available */
  int printf(const char *format, ...);
  int puts(const char *s);
  int putchar(int c);
#endif
#if defined(__has_include)
  #if __has_include(<stdint.h>)
    #include <stdint.h>
  #else
    /* Minimal fixed-width integer types when <stdint.h> is not available */
    typedef signed char int8_t;
    typedef short int16_t;
    typedef int int32_t;
    typedef long long int64_t;
    typedef unsigned char uint8_t;
    typedef unsigned short uint16_t;
    typedef unsigned int uint32_t;
    typedef unsigned long long uint64_t;
  #endif

  #if __has_include(<stdbool.h>)
    #include <stdbool.h>
  #else
    /* Minimal bool type when <stdbool.h> is not available */
    typedef enum { false = 0, true = 1 } bool;
  #endif
#else
  /* Fallback definitions for toolchains without __has_include */
  typedef signed char int8_t;
  typedef short int16_t;
  typedef int int32_t;
  typedef long long int64_t;
  typedef unsigned char uint8_t;
  typedef unsigned short uint16_t;
  typedef unsigned int uint32_t;
  typedef unsigned long long uint64_t;
  typedef enum { false = 0, true = 1 } bool;
#endif

// Os headers csr.h e system.h serão gerados pelo LiteX durante o build.
#if defined(__has_include) && __has_include(<generated/csr.h>) && __has_include(<generated/soc.h>)
  #include <generated/csr.h>
  #include <generated/soc.h>
  #if __has_include(<libbase/console.h>)
    #include <libbase/console.h>
  #endif
#else
  /* Fallback stubs when LiteX generated headers are not available.
    These stubs allow local compilation and basic testing; replace them
    with the actual LiteX-generated headers for real hardware. */

  #ifndef CPU_DESCRIPTION
  #define CPU_DESCRIPTION "Unknown-CPU (stub)"
  #endif

  #ifndef DOTP_STUBS_DEFINED
  #define DOTP_STUBS_DEFINED

  /* Vector write stubs */
  static inline void dotp_a0_write(int32_t v) { (void)v; } static inline void dotp_a1_write(int32_t v) { (void)v; }
  static inline void dotp_a2_write(int32_t v) { (void)v; } static inline void dotp_a3_write(int32_t v) { (void)v; }
  static inline void dotp_a4_write(int32_t v) { (void)v; } static inline void dotp_a5_write(int32_t v) { (void)v; }
  static inline void dotp_a6_write(int32_t v) { (void)v; } static inline void dotp_a7_write(int32_t v) { (void)v; }
  static inline void dotp_b0_write(int32_t v) { (void)v; } static inline void dotp_b1_write(int32_t v) { (void)v; }
  static inline void dotp_b2_write(int32_t v) { (void)v; } static inline void dotp_b3_write(int32_t v) { (void)v; }
  static inline void dotp_b4_write(int32_t v) { (void)v; } static inline void dotp_b5_write(int32_t v) { (void)v; }
  static inline void dotp_b6_write(int32_t v) { (void)v; } static inline void dotp_b7_write(int32_t v) { (void)v; }

  /* Control/result stubs */
  static inline void dotp_start_write(uint32_t v) { (void)v; }
  static inline uint32_t dotp_done_read(void) { return 1U; } /* pretend hardware is immediately done */
  static inline uint32_t dotp_result_lo_read(void) { return 0U; }
  static inline uint32_t dotp_result_hi_read(void) { return 0U; }

  #endif /* DOTP_STUBS_DEFINED */
#endif

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
    // Nota: o nome gerado pelo LiteX para leitura de um CSRStatus(1, name="done")
    // normalmente é dotp_done_read(). Ajuste aqui caso seu csr.h gere um nome diferente.
    return dotp_done_read();
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
  printf("Software: 0x%016llX\n", (unsigned long long)sw);

    // Hardware
    hw_write_vectors(A, B);
    hw_start();
  while (!hw_done());
  int64_t hw = hw_result();
  printf("Hardware: 0x%016llX\n", (unsigned long long)hw);

  if (hw == sw) printf("[OK] Resultado coincide!\n");
  else          printf("[ERRO] Resultado diferente!\n");

    // Loop simples para observar via UART
  while (1) { /* idle */ }
    return 0;
}
