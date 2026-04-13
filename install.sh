#!/bin/bash

# --- Configuración ---
REPO="itsFDavid/nestc"
BINARY_NAME="nestc"
INSTALL_DIR="/usr/local/bin"

echo -e "\033[35m[Nest-C]\033[0m Iniciando instalador global..."

# 1. Detectar Sistema Operativo y Arquitectura
OS_TYPE=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH_TYPE=$(uname -m)

# Mapeo de nombres para coincidir con tus binarios de GitHub
case "$OS_TYPE" in
    darwin)  OS="macos" ;;
    linux)   OS="linux" ;;
    *)       echo " Sistema no soportado: $OS_TYPE"; exit 1 ;;
esac

case "$ARCH_TYPE" in
    x86_64) ARCH="x86_64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *)      echo " Arquitectura no soportada: $ARCH_TYPE"; exit 1 ;;
esac

# Nombre exacto que subiste a GitHub Assets
TARGET_ASSET="nestc-${OS}-${ARCH}"

echo -e "\033[36m[Info]\033[0m Sistema detectado: $OS ($ARCH)"
echo -e "\033[36m[Info]\033[0m Buscando binario: $TARGET_ASSET"

# 2. Obtener la URL de descarga de la última Release usando el API de GitHub
URL=$(curl -s https://api.github.com/repos/$REPO/releases/latest \
    | grep "browser_download_url" \
    | grep "$TARGET_ASSET" \
    | cut -d '"' -f 4)

if [ -z "$URL" ]; then
    echo -e "\033[31m[Error]\033[0m No se encontró un binario para tu arquitectura en la versión v1.0.0."
    exit 1
fi

# 3. Descarga a carpeta temporal
echo -e "\033[36m[Info]\033[0m Descargando desde GitHub..."
curl -L -o /tmp/$BINARY_NAME "$URL"

# 4. Instalación
echo -e "\033[36m[Info]\033[0m Moviendo a $INSTALL_DIR (se requiere sudo)..."
sudo mv /tmp/$BINARY_NAME "$INSTALL_DIR/$BINARY_NAME"
sudo chmod +x "$INSTALL_DIR/$BINARY_NAME"

# 5. Éxito y Primeros pasos
if command -v nestc >/dev/null 2>&1; then
    echo -e "\n\033[32m Nest-C instalado correctamente!\033[0m"
    echo -e "Prueba ejecutando: \033[33mnestc doctor\033[0m"
else
    echo -e "\n\033[31m Error en la instalación.\033[0m Asegúrate de que $INSTALL_DIR esté en tu PATH."
fi