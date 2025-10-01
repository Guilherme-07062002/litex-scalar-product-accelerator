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

download() {
  local url="$1" out="$2"
  if command -v curl >/dev/null 2>&1; then
    echo "Baixando (curl) oss-cad-suite de: $url"
    # --http1.1 evita alguns problemas de HTTP/2; -C - permite resume; --retry para robustez
    curl -L --fail --http1.1 --retry 5 --retry-delay 3 -C - -o "$out" "$url" && return 0
    echo "Aviso: curl falhou, tentando wget..."
  fi
  if command -v wget >/dev/null 2>&1; then
    echo "Baixando (wget) oss-cad-suite de: $url"
    wget -c -O "$out" "$url" && return 0
  fi
  echo "Erro: nem curl nem wget conseguiram baixar o arquivo."
  return 1
}

extract() {
  local tarfile="$1" dest="$2"
  if ! command -v tar >/dev/null 2>&1; then
    echo "Erro: 'tar' não encontrado. Instale tar e tente novamente."
    return 2
  fi
  rm -rf "$dest"
  mkdir -p "$dest"
  echo "Extraindo para $dest ..."
  tar -xzf "$tarfile" -C "$dest" --strip-components=1
}

download "$URL" "$TMP_TGZ"

if [[ ! -s "$TMP_TGZ" ]]; then
  echo "Erro: arquivo baixado está ausente ou vazio: $TMP_TGZ"
  exit 3
fi

extract "$TMP_TGZ" "$DEST_DIR"
rm -f "$TMP_TGZ"

echo "Instalação concluída. Para usar nesta sessão:"
echo "  source $DEST_DIR/environment"
echo "Para tornar permanente, adicione ao seu ~/.bashrc:"
echo "  echo 'source $DEST_DIR/environment' >> ~/.bashrc"

echo "Ferramentas esperadas após ativação: yosys, nextpnr-ecp5, ecppack, openFPGALoader (se incluído na build)."
