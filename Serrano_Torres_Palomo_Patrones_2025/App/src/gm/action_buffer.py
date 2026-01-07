"""Action buffer processing extracted from GameManager.

This module exposes a single entry: process_action_buffer(gm, max_per_frame=5)
which mirrors the previous GameManager.process_action_buffer behavior but keeps
the logic isolated for easier testing and maintenance.
"""
from collections import deque


def process_action_buffer(gm, max_per_frame: int = 5):
    """Process up to ``max_per_frame`` queued upgrade actions.

    The function mutates ``gm.action_buffer`` (expected to be a
    :class:`collections.deque`) and dispatches individual actions to the
    specialised helpers defined in this module. It returns ``None``.
    """
    to_process = min(max_per_frame, len(gm.action_buffer))
    applied_this_frame = set()
    for _ in range(to_process):
        action = gm.action_buffer.popleft()
        ok = False
        if action.get('type') == 'speed':
            try:
                ok = _apply_speed_action(gm)
            except Exception:
                ok = False
        elif action.get('type') == 'eff':
            try:
                ok = _apply_eff_action(gm)
            except Exception:
                ok = False
        elif action.get('type') == 'mine':
            try:
                ok = _apply_mine_action(gm)
            except Exception:
                ok = False

        if ok:
            applied_this_frame.add(action.get('type'))
            # avoid applying more than one successful upgrade of any type per frame
            break

        # failed to apply: retry later unless too many tries
        action['tries'] = action.get('tries', 0) + 1
        if action['tries'] < action.get('max_tries', 30):
            gm.action_buffer.append(action)
        else:
            try:
                print(f"Dropping action {action.get('type')} after {action['tries']} failed tries")
            except Exception:
                pass


def _apply_speed_action(gm) -> bool:
    """Attempt to apply a single global speed upgrade.

    Returns True on success, False to retry later.
    """
    convs = list(getattr(gm, 'conveyors', []))
    if not convs:
        return False

    try:
        next_cost = int(gm.speed_costs[gm.speed_uses_used]) if 0 <= gm.speed_uses_used < len(gm.speed_costs) else None
    except Exception:
        next_cost = None

    if next_cost is None or getattr(gm, 'points', 0) < (next_cost or 0):
        print("[Action] Not enough points to apply Speed upgrade; will retry")
        return False

    prospective_uses = gm.speed_uses_used + 1
    multiplier = 0.9 ** prospective_uses

    applied = 0
    for conv in convs:
        try:
            base_conv = conv
            while hasattr(base_conv, 'target'):
                base_conv = base_conv.target
            if not hasattr(base_conv, '_base_travel_time'):
                base_conv._base_travel_time = getattr(base_conv, 'travel_time', 2000)
            base_conv.travel_time = max(50, int(base_conv._base_travel_time * multiplier))
            applied += 1
        except Exception:
            pass

    if applied > 0:
        try:
            if not hasattr(gm, '_base_production_interval'):
                gm._base_production_interval = 2000
            gm.production_interval = max(100, int(gm._base_production_interval * multiplier))
        except Exception:
            pass
        gm.speed_uses_used += 1
        gm.speed_uses_left = max(0, 10 - gm.speed_uses_used)
        if next_cost is not None:
            try:
                gm.points = max(0, int(gm.points) - int(next_cost))
            except Exception:
                try:
                    gm.points -= next_cost
                except Exception:
                    pass
        try:
            gm._popup_message = f"Mejora Velocidad aplicada ({gm.speed_uses_left})"
            gm._popup_timer = 3000
        except Exception:
            pass
        try:
            print(f"[Action] Speed upgrade applied (uses left={gm.speed_uses_left}) -> updated {applied} conveyors | -{next_cost} pts (total={gm.points})")
        except Exception:
            pass
        return True

    return False


def _apply_eff_action(gm) -> bool:
    """Attempt to apply a single global efficiency upgrade."""
    mines_found = False
    for y, row in enumerate(gm.map.cells):
        for x, cell in enumerate(row):
            if cell and not cell.isEmpty():
                s = cell.structure
                base_s = s
                try:
                    while hasattr(base_s, 'target'):
                        base_s = base_s.target
                except Exception:
                    pass
                if hasattr(base_s, 'number'):
                    mines_found = True
                    break
        if mines_found:
            break

    if not mines_found:
        return False

    try:
        next_cost = int(gm.eff_costs[gm.eff_uses_used]) if 0 <= gm.eff_uses_used < len(gm.eff_costs) else None
    except Exception:
        next_cost = None

    if next_cost is None or getattr(gm, 'points', 0) < (next_cost or 0):
        print("[Action] Not enough points to apply Efficiency upgrade; will retry")
        return False

    applied = 0
    for y, row in enumerate(gm.map.cells):
        for x, cell in enumerate(row):
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
                        base_s._base_number = int(base_s._base_number) + 1
                        base_s._effective_number = max(1, int(base_s._base_number))
                        applied += 1
                    except Exception:
                        pass
                if hasattr(base_s, 'consumingNumber'):
                    if not hasattr(base_s, '_base_consumingNumber'):
                        try:
                            base_s._base_consumingNumber = int(base_s.consumingNumber)
                        except Exception:
                            base_s._base_consumingNumber = getattr(base_s, 'consumingNumber', 1)
                    try:
                        base_s._base_consumingNumber = int(base_s._base_consumingNumber) + 1
                        base_val = max(1, int(base_s._base_consumingNumber))
                        base_s.consumingNumber = base_val
                        try:
                            if s is not base_s and hasattr(s, 'consumingNumber'):
                                s.consumingNumber = base_val
                        except Exception:
                            pass
                        applied += 1
                    except Exception:
                        pass

    if applied > 0:
        try:
            delta = 1
            for conv in getattr(gm, 'conveyors', []):
                try:
                    for item in conv.queue:
                        try:
                            item['value'] = int(item.get('value', 0)) + delta
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
        gm.eff_uses_used += 1
        gm.eff_uses_left = max(0, 10 - gm.eff_uses_used)
        if next_cost is not None:
            try:
                gm.points = max(0, int(gm.points) - int(next_cost))
            except Exception:
                try:
                    gm.points -= next_cost
                except Exception:
                    pass
        try:
            gm._popup_message = f"Mejora Eficiencia aplicada ({gm.eff_uses_left})"
            gm._popup_timer = 3000
        except Exception:
            pass
        try:
            print(f"[Action] Efficiency upgrade applied (uses left={gm.eff_uses_left}) -> updated {applied} mines | -{next_cost} pts (total={gm.points})")
        except Exception:
            pass
        return True

    return False


def _apply_mine_action(gm) -> bool:
    """Attempt to purchase and create a new mine in a random empty cell.

    The original create_new_mine() remains on GameManager; this helper calls
    gm.create_new_mine() and commits purchase on success.
    """
    try:
        next_cost = int(gm.mine_costs[gm.mine_uses_used]) if 0 <= gm.mine_uses_used < len(gm.mine_costs) else None
    except Exception:
        next_cost = None

    if next_cost is None or getattr(gm, 'points', 0) < (next_cost or 0):
        print("[Action] Not enough points to purchase Mine; will retry")
        return False

    created = False
    try:
        created = gm.create_new_mine()
    except Exception:
        created = False

    if not created:
        print("[Action] Failed to place Mine; will retry")
        return False

    try:
        gm.mine_uses_used = int(getattr(gm, 'mine_uses_used', 0)) + 1
        if next_cost is not None:
            try:
                gm.points = max(0, int(gm.points) - int(next_cost))
            except Exception:
                try:
                    gm.points -= next_cost
                except Exception:
                    pass
        if getattr(gm, 'hud', None):
            try:
                gm.hud.show_popup("Mina creada")
            except Exception:
                pass
        try:
            print(f"[Action] Mine purchase applied | -{next_cost} pts (total={gm.points})")
        except Exception:
            pass
        return True
    except Exception:
        return True
