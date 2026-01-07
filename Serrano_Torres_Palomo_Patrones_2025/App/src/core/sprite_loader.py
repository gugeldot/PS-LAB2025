import pathlib
import pygame as pg


def load_sprite_from_assets(filename: str, size=(40, 40)):
    """Try to load a sprite from the project Assets/Sprites folder.

    Returns a pygame.Surface or None if loading failed. Exceptions are
    caught and printed as warnings to avoid breaking the game flow.
    """
    try:
        base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
        sprite_path = base_dir / "Assets" / "Sprites" / filename
        if sprite_path.exists():
            surf = pg.image.load(str(sprite_path)).convert_alpha()
            surf = pg.transform.scale(surf, size)
            return surf
        else:
            # Not an error; caller can fallback to drawing shapes
            print(f"Warning: sprite not found at {sprite_path}")
    except Exception as e:
        print(f"Warning: Could not load sprite {filename}: {e}")
    return None
