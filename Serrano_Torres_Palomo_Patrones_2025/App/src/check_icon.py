import pygame as pg
import pathlib

def check_icon():
    base_dir = pathlib.Path(__file__).resolve().parent
    app_dir = base_dir.parent
    icon_path = app_dir / "Assets" / "icon.png"

    print(f"[ICON CHECK] icon path: {icon_path}")
    print(f"[ICON CHECK] exists: {icon_path.exists()}")

    try:
        # pg.image.load can work without opening a window if SDL_image supports it
        img = pg.image.load(str(icon_path))
        print(f"[ICON CHECK] loaded: {type(img)}")
    except Exception as e:
        print(f"[ICON CHECK] failed to load icon: {e}")

if __name__ == '__main__':
    check_icon()
