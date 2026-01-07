from .update_helpers import update as _update_impl


def update(gm):
    """Thin wrapper that delegates the update logic to `update_helpers.update`.

    Keeps the same public `gm_update.update(gm)` entrypoint.
    """
    _update_impl(gm)
