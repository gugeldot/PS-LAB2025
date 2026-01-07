Distribuciones (dist)
=====================

Contenido creado:

- dist/linux/         -> carpeta donde irá el binario Linux (onefile)
- dist/windows/       -> carpeta donde irá el binario Windows (.exe)
- build_linux.sh      -> script para construir localmente en Linux usando PyInstaller
- build_windows.sh    -> helper para builds en Windows (ejecutar en Windows) o usar CI

Instrucciones rápidas (Linux)
-----------------------------

1) Sitúate en la carpeta `App/`.
2) Haz ejecutable el script y ejecútalo:

   chmod +x dist/build_linux.sh
   ./dist/build_linux.sh

El script creará un entorno virtual `.venv_build`, instalará dependencias y PyInstaller, y generará un binario "onefile" en `dist/linux/`.

Notas importantes
-----------------

- Construir un .exe de Windows desde Linux no es confiable sin herramientas adicionales (Wine, mingw, cross-compile) y se recomienda:
  - Ejecutar `dist/build_windows.sh` desde Windows (Git Bash / PowerShell) con Python instalado, o
  - Usar CI (GitHub Actions) que compile en `windows-latest` y suba el artefacto.

- PyInstaller `--add-data` usa separador `:` en Linux/macOS y `;` en Windows. Los scripts manejan esto.

- Si tu aplicación carga assets por rutas relativas, asegúrate de ejecutarla desde la ubicación correcta o adapta el código para localizar los recursos cuando se ejecuta desde un único binario.

Sugerencia (CI)
---------------

Si quieres que yo añada un workflow de GitHub Actions para crear ambos binarios automáticamente (Linux y Windows) y subirlos como artefactos, dímelo y lo añado.
