import sys
import pathlib


# APP_ROOT (resource root) points to the folder where bundled resources
# live. When running as a PyInstaller onefile bundle, that's sys._MEIPASS;
# when running from source it's the App/ project root.
#
# APP_DIR is the directory where the binary/executable lives and is the
# recommended place to store writable files (logs, saves). For frozen apps
# use the executable parent; for source runs we default to the project root.
if getattr(sys, "frozen", False):
    # PyInstaller: resources unpacked to _MEIPASS (read-only temporaries)
    APP_ROOT = pathlib.Path(sys._MEIPASS)
    # Directory where executable lives (writable location next to exe)
    APP_DIR = pathlib.Path(sys.executable).parent
else:
    # three levels up from this file -> App/
    APP_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
    APP_DIR = APP_ROOT

__all__ = ["APP_ROOT", "APP_DIR"]
