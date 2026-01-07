import json
import os
from pathlib import Path
from typing import Dict, Optional

from settings import CELL_SIZE_PX
from map.map import Map


"""Persistence helpers to load and save game state.

This module provides two convenience functions, :func:`load_game` and
:func:`save_game`, that operate on a GameManager-like object ``gm``. The
functions expect ``gm.save_file`` and ``gm.save_dir`` to be set (see
``gm_init.init_paths``).

The saved JSON format is conservative: the map grid stores structure class
names and a few base attributes (``number``, ``consumingNumber``). Conveyors
are stored separately with grid start/end coordinates and an optional
``travel_time`` value. The functions attempt to restore upgrade counters and
apply their effects where possible.
"""


def load_game(gm, creators: Dict[str, object]) -> bool:
    """Load map and upgrades into the provided GameManager-like object.

    Args:
        gm: GameManager-like instance where the loaded data will be applied.
        creators: Mapping from structure class name (str) to a creator object
            exposing a ``createStructure((x,y), ...)`` method able to
            re-create structure instances from the saved attributes.

    Returns:
        True on success, False on failure. On success the following side
        effects occur on ``gm``:
        - ``gm.map`` is set to a restored :class:`map.map.Map` instance.
        - ``gm.conveyors`` is set when conveyors are present and a
          ``gameManager``/``gm`` is supplied to the Map loader.
        - Upgrade counters (``speed_uses_used``, ``eff_uses_used``,
          ``mine_uses_used``) and ``gm.points`` are restored when present
          in the save file.
    """
    try:
        if not getattr(gm, 'save_file', None) or not gm.save_file.exists():
            return False
        # load map using existing Map loader
        gm.map = Map.load_from_file(str(gm.save_file), creators=creators, gameManager=gm)

        # restore upgrades & points
        try:
            with open(gm.save_file, 'r', encoding='utf-8') as fh:
                saved = json.load(fh)
                try:
                    gm.points = int(saved.get('score', getattr(gm, 'points', 0)))
                except Exception:
                    gm.points = int(getattr(gm, 'points', 0) or 0)

                upgrades = saved.get('upgrades', {})
                speed_used = int(upgrades.get('speed_uses_used', 0))
                eff_used = int(upgrades.get('eff_uses_used', 0))
                mine_used = int(upgrades.get('mine_uses_used', 0))

                gm.speed_uses_used = speed_used
                gm.eff_uses_used = eff_used
                try:
                    gm.mine_uses_used = mine_used
                    gm.mine_uses_left = None
                except Exception:
                    pass
                gm.speed_uses_left = max(0, 10 - gm.speed_uses_used)
                gm.eff_uses_left = max(0, 10 - gm.eff_uses_used)
        except Exception:
            pass

        # Apply speed/effect upgrades to conveyors and structures if needed
        try:
            if getattr(gm, 'speed_uses_used', 0) > 0:
                multiplier = 0.9 ** gm.speed_uses_used
                for conv in getattr(gm, 'conveyors', []):
                    base_conv = conv
                    while hasattr(base_conv, 'target'):
                        base_conv = base_conv.target
                    if not hasattr(base_conv, '_base_travel_time'):
                        base_conv._base_travel_time = getattr(base_conv, 'travel_time', 2000)
                    base_conv.travel_time = max(50, int(base_conv._base_travel_time * multiplier))
                try:
                    if not hasattr(gm, '_base_production_interval'):
                        gm._base_production_interval = 2000
                    gm.production_interval = max(100, int(gm._base_production_interval * multiplier))
                except Exception:
                    pass
        except Exception:
            pass

        try:
            if getattr(gm, 'eff_uses_used', 0) > 0:
                eff_used = gm.eff_uses_used
                for row in gm.map.cells:
                    for cell in row:
                        if cell and not cell.isEmpty():
                            s = cell.structure
                            base_s = s
                            try:
                                while hasattr(base_s, 'target'):
                                    base_s = base_s.target
                            except Exception:
                                pass
                            if hasattr(base_s, 'number'):
                                if not hasattr(base_s, '_base_number'):
                                    try:
                                        base_s._base_number = int(base_s.number)
                                    except Exception:
                                        base_s._base_number = getattr(base_s, 'number', 1)
                                try:
                                    base_s._eff_number_increase = int(eff_used)
                                except Exception:
                                    base_s._eff_number_increase = getattr(base_s, '_eff_number_increase', 0)
                                base_s._effective_number = max(1, int(base_s._base_number + getattr(base_s, '_eff_number_increase', 0)))
                            if hasattr(base_s, 'consumingNumber'):
                                if not hasattr(base_s, '_base_consumingNumber'):
                                    try:
                                        base_s._base_consumingNumber = int(base_s.consumingNumber)
                                    except Exception:
                                        base_s._base_consumingNumber = getattr(base_s, 'consumingNumber', 1)
                                try:
                                    base_s._eff_consuming_increase = int(eff_used)
                                except Exception:
                                    base_s._eff_consuming_increase = getattr(base_s, '_eff_consuming_increase', 0)
                                base_val = max(1, int(base_s._base_consumingNumber + getattr(base_s, '_eff_consuming_increase', 0)))
                                base_s.consumingNumber = base_val
                                try:
                                    if s is not base_s and hasattr(s, 'consumingNumber'):
                                        s.consumingNumber = base_val
                                except Exception:
                                    pass
        except Exception:
            pass

        return True
    except Exception:
        return False


def save_game(gm):
    """Save the map, conveyors and upgrade info to gm.save_file (like original GameManager.save_map)."""
    try:
        base = gm.map.to_dict()
        # adjust grid entries with canonical/base attributes
        try:
            grid = base.get('grid', [])
            eff_used = int(getattr(gm, 'eff_uses_used', 0))
            for y, row in enumerate(grid):
                for x, entry in enumerate(row):
                    if not entry:
                        continue
                    try:
                        cell = gm.map.getCell(x, y)
                        if cell and not cell.isEmpty():
                            s = cell.structure
                            if 'number' in entry and hasattr(s, '_base_number'):
                                try:
                                    entry['number'] = int(getattr(s, '_base_number'))
                                except Exception:
                                    entry['number'] = int(entry.get('number', 1))
                            if 'consumingNumber' in entry and hasattr(s, '_base_consumingNumber'):
                                try:
                                    entry['consumingNumber'] = int(getattr(s, '_base_consumingNumber'))
                                except Exception:
                                    entry['consumingNumber'] = int(entry.get('consumingNumber', 1))
                    except Exception:
                        pass
        except Exception:
            pass

        convs = []
        for conv in getattr(gm, 'conveyors', []):
            sx = sy = ex = ey = None
            found = False
            for y, row in enumerate(gm.map.cells):
                for x, cell in enumerate(row):
                    if not cell.isEmpty() and hasattr(cell.structure, 'position'):
                        pos = cell.structure.position
                        try:
                            px, py = float(pos.x), float(pos.y)
                        except Exception:
                            px, py = float(pos[0]), float(pos[1])
                        if int(px) == int(conv.start_pos.x) and int(py) == int(conv.start_pos.y):
                            sx, sy = x, y
                            found = True
                            break
                if found:
                    break
            if sx is None:
                sx = int(conv.start_pos.x) // CELL_SIZE_PX
            # Compute end coordinates similarly
            found = False
            for y, row in enumerate(gm.map.cells):
                for x, cell in enumerate(row):
                    if not cell.isEmpty() and hasattr(cell.structure, 'position'):
                        pos = cell.structure.position
                        try:
                            px, py = float(pos.x), float(pos.y)
                        except Exception:
                            px, py = float(pos[0]), float(pos[1])
                        if int(px) == int(conv.end_pos.x) and int(py) == int(conv.end_pos.y):
                            ex, ey = x, y
                            found = True
                            break
                if found:
                    break
            if ex is None:
                ex = int(conv.end_pos.x) // CELL_SIZE_PX
            if ey is None:
                ey = int(conv.end_pos.y) // CELL_SIZE_PX

            travel = getattr(conv, 'travel_time', None)
            if hasattr(conv, '_base_travel_time'):
                try:
                    travel = int(getattr(conv, '_base_travel_time'))
                except Exception:
                    travel = getattr(conv, 'travel_time', None)
            entry = {"start": [sx, sy], "end": [ex, ey], "travel_time": travel}
            convs.append(entry)

        base['conveyors'] = convs
        base['upgrades'] = {
            'speed_uses_used': getattr(gm, 'speed_uses_used', 0),
            'eff_uses_used': getattr(gm, 'eff_uses_used', 0),
            'mine_uses_used': getattr(gm, 'mine_uses_used', 0)
        }
        try:
            base['score'] = int(getattr(gm, 'points', 0))
        except Exception:
            base['score'] = getattr(gm, 'points', 0)

        os.makedirs(gm.save_dir, exist_ok=True)
        with open(gm.save_file, 'w', encoding='utf-8') as fh:
            json.dump(base, fh, indent=2)
        try:
            print(f"Map (with conveyors) saved to {gm.save_file}")
        except Exception:
            pass
        return True
    except Exception as e:
        try:
            print("Failed to save map:", e)
        except Exception:
            pass
        return False
