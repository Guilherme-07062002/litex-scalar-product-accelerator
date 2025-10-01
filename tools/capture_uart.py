#!/usr/bin/env python3
"""
Captura a saída da UART e salva em um arquivo de log.

Exemplo:
  python tools/capture_uart.py --port /dev/ttyUSB0 --baud 115200 --out docs/uart_log.txt

Pressione Ctrl+C para encerrar manualmente.
"""
import argparse
import sys
import time

try:
    import serial
except ImportError:
    print("Erro: módulo pyserial não encontrado. Instale com: pip install pyserial")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Captura UART -> arquivo de log")
    parser.add_argument("--port", required=True, help="Porta serial (ex.: /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate (default: 115200)")
    parser.add_argument("--out", default="docs/uart_log.txt", help="Arquivo de saída")
    parser.add_argument("--timeout", type=float, default=0.2, help="Timeout de leitura em segundos")
    parser.add_argument("--append", action="store_true", help="Acrescenta ao arquivo em vez de sobrescrever")
    args = parser.parse_args()

    mode = "ab" if args.append else "wb"

    print(f"Abrindo porta {args.port} @ {args.baud} baud...")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=args.timeout)
    except Exception as e:
        print(f"Falha ao abrir {args.port}: {e}")
        sys.exit(1)

    print(f"Gravando em {args.out}. Pressione Ctrl+C para parar.")
    with open(args.out, mode) as f:
        try:
            while True:
                data = ser.read(1024)
                if data:
                    # Normaliza quebras de linha para \n no arquivo
                    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                    f.write(data)
                    f.flush()
                    # Também ecoa no console
                    try:
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                    except Exception:
                        pass
                else:
                    # Pequeno descanso para não ocupar 100% CPU
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nCaptura encerrada pelo usuário.")
        finally:
            ser.close()


if __name__ == "__main__":
    main()
