#!/usr/bin/env bash
# Instalação rápida da toolchain ECP5 (oss-cad-suite) em tools/oss-cad-suite
# Uso:
#   ./tools/install_ecp5_toolchain.sh <URL_DO_ARQUIVO_TGZ_DO_OSS_CAD_SUITE>
# Exemplo de URL (verifique a release mais recente):
#   https://github.com/YosysHQ/oss-cad-suite-build/releases
#   https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-12-20/oss-cad-suite-linux-x64-20241220.tgz
#
# Após instalar, adicione ao PATH (sessão atual):
#   source tools/oss-cad-suite/environment
# Ou persista em ~/.bashrc:
#   echo 'source $(pwd)/tools/oss-cad-suite/environment' >> ~/.bashrc

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <URL_DO_OSS_CAD_SUITE_TGZ>"
  exit 1
fi

URL="$1"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST_DIR="$ROOT_DIR/tools/oss-cad-suite"
TMP_TGZ="$ROOT_DIR/tools/oss-cad-suite.tgz"

mkdir -p "$ROOT_DIR/tools"

if ! command -v curl >/dev/null 2>&1; then
  echo "Erro: curl não encontrado. Instale curl e tente novamente."
  exit 2
fi

echo "Baixando oss-cad-suite de: $URL"
curl -L "$URL" -o "$TMP_TGZ"

rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

echo "Extraindo para $DEST_DIR ..."
tar -xzf "$TMP_TGZ" -C "$DEST_DIR" --strip-components=1
rm -f "$TMP_TGZ"

echo "Instalação concluída. Para usar nesta sessão:"
echo "  source $DEST_DIR/environment"
echo "Para tornar permanente, adicione ao seu ~/.bashrc:"
echo "  echo 'source $DEST_DIR/environment' >> ~/.bashrc"

echo "Ferramentas esperadas após ativação: yosys, nextpnr-ecp5, ecppack, openFPGALoader (se incluído na build)."
