import pygame as pg
import pathlib

def check_music():
    base_dir = pathlib.Path(__file__).resolve().parent
    app_dir = base_dir.parent
    music_path = app_dir / "Assets" / "Music" / "kirbySoundTrack.mp3"

    print(f"[CHECK] music path: {music_path}")
    print(f"[CHECK] exists: {music_path.exists()}")

    try:
        try:
            pg.mixer.init()
            print("[CHECK] mixer.init() succeeded")
        except Exception as e:
            print(f"[CHECK] mixer.init() failed: {e}")
            try:
                print(f"[CHECK] pg.mixer.get_init(): {pg.mixer.get_init()}")
            except Exception:
                pass

        if music_path.exists() and pg.mixer.get_init():
            try:
                pg.mixer.music.load(str(music_path))
                print("[CHECK] music loaded ok")
                pg.mixer.music.set_volume(0.6)
                pg.mixer.music.play(-1)
                print(f"[CHECK] music playing? {pg.mixer.music.get_busy()}")
            except Exception as e:
                print(f"[CHECK] failed to load/play: {e}")
    except Exception as e:
        print(f"[CHECK] unexpected error: {e}")

if __name__ == '__main__':
    check_music()
