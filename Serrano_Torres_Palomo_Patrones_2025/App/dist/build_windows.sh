#!/usr/bin/env bash
set -euo pipefail

# Obtener la ruta raíz del proyecto (un nivel arriba de donde está el script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Detectar entorno Windows
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    echo "--- Iniciando build para Windows ---"

    # 1. Limpiar builds anteriores para evitar errores de caché
    echo "Limpiando archivos temporales..."
    rm -rf build dist/windows GameApp.spec

    # 2. Configurar entorno virtual
    python -m venv .venv_build
    
    # Soporte para diferentes shells en Windows
    if [ -f ".venv_build/Scripts/activate" ]; then
        source .venv_build/Scripts/activate
    else
        source .venv_build/bin/activate
    fi

    # 3. Instalar dependencias
    python -m pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
    pip install pyinstaller

    # 4. Preparar rutas para PyInstaller (Formato Windows Nativo)
    # Esto convierte /c/Users/... a C:\Users\...
    WIN_ROOT_DIR=$(cygpath -w "$ROOT_DIR")
    ASSETS_PATH="${WIN_ROOT_DIR}\\Assets"
    MAIN_PY="${WIN_ROOT_DIR}\\src\\main.py"

    echo "Ruta de Assets: $ASSETS_PATH"

    # 5. Ejecutar PyInstaller
    # MSYS_NO_PATHCONV=1 evita que Git Bash altere el separador ';'
    PYINSTALLER_NAME="NumberTycoon"
    
    echo "Ejecutando PyInstaller..."
    MSYS_NO_PATHCONV=1 pyinstaller --noconfirm --onefile \
      --name "$PYINSTALLER_NAME" \
      --add-data "$ASSETS_PATH;Assets" \
      --paths "src" \
      --distpath "dist/windows" \
      --workpath "build" \
      --specpath "build" \
      "$MAIN_PY"

    echo "-------------------------------------------------------"
    echo "Build finalizado con éxito."
    echo "Ejecutable en: dist/windows/$PYINSTALLER_NAME.exe"
    echo "-------------------------------------------------------"
    ;;
    
  *)
    echo "Error: Este script debe ejecutarse en Windows (Git Bash)."
    exit 1
    ;;
esac