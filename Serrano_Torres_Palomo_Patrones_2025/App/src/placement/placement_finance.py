"""Helpers to compute build cost/refund while avoiding repeated code.

Behavior is intentionally conservative: look into gameManager.build_costs (if
present) for a cost keyed by a type name (sum, mul, div, splitter, merger,
conveyor). If a matching substring is found in the class name, use the
mapping's value (falling back to the object's .getCost()). If no mapping or
no match, fall back to object's .getCost(). Any exceptions result in 0.
"""


_MAP_KEY_ORDER = [
    ("sum", "sum"),
    ("mul", "mul"),
    ("multiply", "mul"),
    ("div", "div"),
    ("splitter", "splitter"),
    ("merger", "merger"),
    ("conveyor", "conveyor"),
    ("convey", "conveyor"),
]


def _compute_from_mapping(costs_map, type_name, get_cost_callable):
    """Return integer cost using costs_map and type_name heuristics.

    - costs_map: dict-like mapping of keys to numeric cost (may be empty)
    - type_name: lowercased class/name to search for substrings
    - get_cost_callable: callable that returns the fallback cost (may raise)

    Returns an int cost (or raises nothing; on any failure returns 0).
    """
    try:
        if costs_map:
            # find first matching substring and use mapped key as priority
            for substr, key in _MAP_KEY_ORDER:
                if substr in type_name:
                    return int(costs_map.get(key, get_cost_callable()))
        # no mapping entry matched; fallback to object's cost
        return int(get_cost_callable())
    except Exception:
        try:
            return int(get_cost_callable())
        except Exception:
            return 0


def compute_cost(controller):
    """Return integer cost for the current factory, preserving original fallbacks."""
    try:
        costs_map = getattr(controller.gameManager, "build_costs", None) or {}
        cname = controller.factory.__class__.__name__.lower() if controller.factory is not None else ""
        return _compute_from_mapping(costs_map, cname, lambda: controller.factory.getCost())
    except Exception:
        try:
            return int(controller.factory.getCost())
        except Exception:
            return 0


def compute_refund(controller, structure):
    """Return integer refund for a structure, mirroring original behaviour."""
    try:
        costs_map = getattr(controller.gameManager, "build_costs", None) or {}
        sname = structure.__class__.__name__.lower()
        return _compute_from_mapping(costs_map, sname, lambda: structure.getCost())
    except Exception:
        try:
            return int(structure.getCost())
        except Exception:
            return 0
