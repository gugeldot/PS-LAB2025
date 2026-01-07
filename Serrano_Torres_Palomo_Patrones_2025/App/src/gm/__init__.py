"""gm package: thin adapters and helpers for the game's GameManager logic.

This package groups update/draw/persistence and upgrade implementation
helpers. The modules are thin wrappers around helper implementations so the
public API used by the rest of the project remains stable.
"""

__all__ = [
    'action_buffer', 'gm_draw', 'gm_init', 'gm_update', 'gm_upgrades',
    'persistence', 'renderer', 'update_helpers', 'upgrades_impl'
]
