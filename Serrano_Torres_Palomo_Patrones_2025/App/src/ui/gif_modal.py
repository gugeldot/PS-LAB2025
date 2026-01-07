"""GIF modal helper used by the HUD.

This module implements :class:`GifModal`, a small helper that loads GIF
files from the game's Assets/gifs folder, converts frames to pygame
surfaces and exposes a simple modal API used by the HUD:

- open(start_index=0), close(), next(), prev()
- update(dt_ms), draw(screen)
- readable attributes: active, files, titles, index, frames,
  frame_durations, frame_index, frame_timer
- buttons: prev_button, next_button, exit_button (pygame.Rect or None)
"""

import pathlib
import pygame as pg
from settings import WIDTH, HEIGHT
try:
    from PIL import Image, ImageSequence
except Exception:
    Image = None
from utils.app_paths import APP_ROOT as BASE_DIR


class GifModal:
    """Modal controller that displays GIFs as an in-game tutorial/gallery.

    The class is intentionally tolerant: if Pillow is missing it falls back
    to loading a single static surface via ``pygame.image.load``. Frames and
    durations are stored in ``frames`` and ``frame_durations`` respectively.
    """

    def __init__(self, game=None, base_path: pathlib.Path = None):
        self.game = game
        if base_path is None:
            self.base = BASE_DIR
        else:
            self.base = pathlib.Path(base_path)

        self.gif_dir = self.base / "Assets" / "gifs"

        # state
        self.active = False
        self.files = []
        self.titles = []
        self.index = 0
        self.frames = []
        self.frame_durations = []
        self.frame_index = 0
        self.frame_timer = 0

        # modal UI buttons (created during draw)
        self.prev_button = None
        self.next_button = None
        self.exit_button = None

    def open(self, start_index: int = 0):
        try:
            if not self.gif_dir.exists() or not self.gif_dir.is_dir():
                self.files = []
                return

            order = None
            try:
                order = getattr(self.game, 'gifs_order', None)
            except Exception:
                order = None

            files = []
            titles = []
            if order and isinstance(order, (list, tuple)) and len(order) > 0:
                for entry in order:
                    try:
                        if isinstance(entry, (list, tuple)) and len(entry) >= 1:
                            fname = str(entry[0])
                            title = str(entry[1]) if len(entry) >= 2 else None
                        else:
                            fname = str(entry)
                            title = None
                        p = self.gif_dir / fname
                        if p.exists() and p.is_file():
                            files.append(p)
                            titles.append(title if title is not None else p.stem)
                    except Exception:
                        pass

            if not files:
                scanned = sorted([p for p in self.gif_dir.iterdir() if p.suffix.lower() in ('.gif',)])
                files = scanned
                titles = [p.stem for p in scanned]

            if not files:
                self.files = []
                self.titles = []
                return

            self.files = files
            self.titles = titles
            self.index = max(0, min(start_index, len(self.files) - 1))
            self._load_current_gif_frames()
            self.active = True
            self.frame_index = 0
            self.frame_timer = 0
            try:
                if hasattr(self, 'game') and self.game is not None:
                    setattr(self.game, '_tutorial_paused', True)
            except Exception:
                pass
        except Exception:
            self.files = []
            self.active = False

    def close(self):
        try:
            self.active = False
            self.files = []
            self.frames = []
            self.frame_durations = []
            self.prev_button = None
            self.next_button = None
            self.exit_button = None
            try:
                if hasattr(self, 'game') and self.game is not None:
                    setattr(self.game, '_tutorial_paused', False)
            except Exception:
                pass
        except Exception:
            pass

    def next(self):
        try:
            if not self.files:
                return
            self.index = (self.index + 1) % len(self.files)
            self._load_current_gif_frames()
            self.frame_index = 0
            self.frame_timer = 0
        except Exception:
            pass

    def prev(self):
        try:
            if not self.files:
                return
            self.index = (self.index - 1) % len(self.files)
            self._load_current_gif_frames()
            self.frame_index = 0
            self.frame_timer = 0
        except Exception:
            pass

    def _load_current_gif_frames(self):
        self.frames = []
        self.frame_durations = []
        try:
            path = self.files[self.index]
        except Exception:
            return

        if Image is None:
            try:
                surf = pg.image.load(str(path)).convert_alpha()
                self.frames = [surf]
                self.frame_durations = [100]
            except Exception:
                self.frames = []
                self.frame_durations = []
            return

        try:
            img = Image.open(str(path))
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(img):
                try:
                    f = frame.convert('RGBA')
                    data = f.tobytes()
                    size = f.size
                    try:
                        surf = pg.image.fromstring(data, size, 'RGBA')
                    except Exception:
                        surf = pg.Surface(size, pg.SRCALPHA)
                    dur = frame.info.get('duration', img.info.get('duration', 100))
                    try:
                        dur = int(dur)
                    except Exception:
                        dur = 100
                    frames.append(surf)
                    durations.append(dur)
                except Exception:
                    continue

            if frames:
                self.frames = frames
                self.frame_durations = durations
                return
        except Exception:
            try:
                surf = pg.image.load(str(path)).convert_alpha()
                self.frames = [surf]
                self.frame_durations = [100]
            except Exception:
                self.frames = []
                self.frame_durations = []

    def update(self, dt_ms: int):
        if not self.active or not self.frames:
            return
        self.frame_timer += dt_ms
        if self.frame_durations:
            dur = self.frame_durations[self.frame_index]
        else:
            dur = 100
        if self.frame_timer >= dur:
            self.frame_timer -= dur
            self.frame_index = (self.frame_index + 1) % max(1, len(self.frames))

    def draw(self, screen):
        if not self.active or not self.frames:
            return

        surf = self.frames[self.frame_index]
        sw, sh = surf.get_size()
        maxw = min(sw, WIDTH - 120)
        maxh = min(sh, HEIGHT - 160)
        if sw > maxw or sh > maxh:
            scale = min(maxw / sw, maxh / sh)
            new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
            try:
                surf = pg.transform.smoothscale(surf, new_size)
            except Exception:
                surf = pg.transform.scale(surf, new_size)
            sw, sh = new_size

        x = (WIDTH - sw) // 2
        y = 80
        screen.blit(surf, (x, y))

        bw = 40
        bh = 30
        pad = 10
        self.prev_button = pg.Rect(x - bw - pad, y + sh//2 - bh//2, bw, bh)
        self.next_button = pg.Rect(x + sw + pad, y + sh//2 - bh//2, bw, bh)
        self.exit_button = pg.Rect(x + sw - bw, y - bh - pad, bw, bh)

        pg.draw.rect(screen, (200,200,200), self.prev_button)
        pg.draw.rect(screen, (200,200,200), self.next_button)
        pg.draw.rect(screen, (255,100,100), self.exit_button)

        try:
            title = self.titles[self.index]
        except Exception:
            title = ''
        font = pg.font.Font(None, 20)
        text = font.render(str(title), True, (30,30,30))
        tx = x + (sw - text.get_width())//2
        ty = y + sh + 8
        screen.blit(text, (tx, ty))
