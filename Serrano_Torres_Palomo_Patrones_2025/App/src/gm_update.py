import pygame as pg
from settings import *
from gm_upgrades import process_action_buffer


def update(gm):
    # update inputs
    gm.mouse.update()
    gm.state.update()
    # popup timer
    try:
        if hasattr(gm, '_popup_timer') and getattr(gm, '_popup_timer', 0) is not None:
            try:
                gm._popup_timer -= int(gm.delta_time)
            except Exception:
                gm._popup_timer -= 0
            if gm._popup_timer <= 0:
                try:
                    gm._popup_timer = None
                    gm._popup_message = None
                except Exception:
                    pass
    except Exception:
        pass

    # process action buffer
    try:
        process_action_buffer(gm)
    except Exception:
        pass

    # camera movement
    try:
        keys = pg.key.get_pressed()
        if keys[pg.K_w] or keys[pg.K_UP]:
            gm.camera.y = max(0, gm.camera.y - gm.camera_speed * (gm.delta_time / 1000.0))
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            max_y = max(0, gm.map.height * CELL_SIZE_PX - HEIGHT)
            gm.camera.y = min(max_y, gm.camera.y + gm.camera_speed * (gm.delta_time / 1000.0))
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            gm.camera.x = max(0, gm.camera.x - gm.camera_speed * (gm.delta_time / 1000.0))
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            max_x = max(0, gm.map.width * CELL_SIZE_PX - WIDTH)
            gm.camera.x = min(max_x, gm.camera.x + gm.camera_speed * (gm.delta_time / 1000.0))
    except Exception:
        pass

    # update map structures
    gm.map.update()

    # update conveyors
    for conv in getattr(gm, 'conveyors', []):
        try:
            conv.update()
        except Exception:
            pass

    # production interval
    if not hasattr(gm, '_base_production_interval'):
        gm._base_production_interval = 2000
    if not hasattr(gm, 'production_interval'):
        gm.production_interval = int(gm._base_production_interval)

    gm.production_timer += gm.delta_time
    prod_int = int(getattr(gm, 'production_interval', getattr(gm, '_base_production_interval', 2000)))
    if gm.production_timer > prod_int:
        if hasattr(gm, 'mine') and gm.mine and gm.conveyors:
            gm.mine.produce(gm.conveyors[0])
        gm.production_timer = 0

    # immediate consumption at the end of final conveyor
    try:
        if hasattr(gm, 'well') and gm.well and hasattr(gm, 'final_conveyor') and gm.final_conveyor is not None:
            q = getattr(gm.final_conveyor, 'queue', None)
            if q and len(q) > 0 and q[0].get('position', 0) >= 1.0:
                try:
                    gm.well.consume(gm.final_conveyor)
                except Exception:
                    pass
    except Exception:
        pass

    # tick and caption
    gm.delta_time = gm.clock.tick(FPS)
    pg.display.set_caption(f'{gm.clock.get_fps() :.1f}')
