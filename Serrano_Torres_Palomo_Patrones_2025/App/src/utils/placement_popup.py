def notify_destroy_not_allowed(controller, structure):
    """Show HUD/popup notification and return the game to normal state like original code.
    Keeps the many fallbacks from the original method.
    """
    gm = controller.gameManager
    msg = f"No se pueden destruir {structure.__class__.__name__}"
    try:
        if hasattr(gm, 'hud') and getattr(gm, 'hud'):
            try:
                gm.hud.show_popup(msg)
                try:
                    if hasattr(gm, 'hud') and getattr(gm, 'hud'):
                        try:
                            gm.hud.shop_mode = None
                            gm.hud._setup_buttons()
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    if hasattr(gm, 'setState') and hasattr(gm, 'normalState'):
                        gm.setState(gm.normalState)
                except Exception:
                    pass
            except Exception:
                try:
                    gm._popup_message = msg
                    gm._popup_timer = 3000
                    try:
                        if hasattr(gm, 'hud') and getattr(gm, 'hud'):
                            try:
                                gm.hud.shop_mode = None
                                gm.hud._setup_buttons()
                            except Exception:
                                pass
                    except Exception:
                        pass
                    try:
                        if hasattr(gm, 'setState') and hasattr(gm, 'normalState'):
                            gm.setState(gm.normalState)
                    except Exception:
                        pass
                except Exception:
                    pass
        else:
            try:
                gm._popup_message = msg
                gm._popup_timer = 3000
                try:
                    if hasattr(gm, 'hud') and getattr(gm, 'hud'):
                        try:
                            gm.hud.shop_mode = None
                            gm.hud._setup_buttons()
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    if hasattr(gm, 'setState') and hasattr(gm, 'normalState'):
                        gm.setState(gm.normalState)
                except Exception:
                    pass
            except Exception:
                pass
    except Exception:
        pass
