#!/usr/bin/env python3
"""
Converte build/dotp/csr.csv em uma tabela Markdown de CSRs para incluir no README.
"""
import csv
from pathlib import Path

def main():
    csv_path = Path('build/dotp/csr.csv')
    if not csv_path.exists():
        print("csr.csv não encontrado. Rode o build do SoC primeiro.")
        return
    rows = []
    with csv_path.open() as f:
        rdr = csv.reader(f)
        for r in rdr:
            # Formato típico: name, address, size, rw
            if not r or r[0].startswith('#'):
                continue
            if len(r) < 4:
                continue
            name, addr, size, access = r[0], r[1], r[2], r[3]
            rows.append((name, addr, size, access))

    # Filtra apenas o bloco dotp
    rows = [r for r in rows if r[0].startswith('dotp_')]
    # Gera Markdown
    print("| Nome | Endereço | Tamanho | Acesso |")
    print("|------|----------|---------|--------|")
    for name, addr, size, access in rows:
        print(f"| {name} | {addr} | {size} | {access} |")

if __name__ == '__main__':
    main()
