import pygame as pg
from settings import *
from gm_upgrades import process_action_buffer


def update(gm):
    # update inputs
    gm.mouse.update()
    gm.state.update()
    # (Popup timer handled by HUD.update called after delta_time is computed)

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
        # Iterar sobre todas las estructuras para encontrar minas y producir
        structures = getattr(gm, 'structures', [])
        for struct in structures:
            if struct.__class__.__name__ == 'Mine':
                # Verificar si tiene cinta de salida conectada
                if hasattr(struct, 'outputConveyor') and struct.outputConveyor:
                    try:
                        struct.produce(struct.outputConveyor)
                    except Exception:
                        pass
        gm.production_timer = 0

    # Consumo inmediato eliminado: ahora se maneja a través de las conexiones
    # Conveyor.update() llama a outputConveyor.push(), que en el caso del Well maneja el consumo.
    
    # Process operation modules (SumModule, MulModule)
    structures = getattr(gm, 'structures', [])
    for struct in structures:
        struct_type = struct.__class__.__name__
        if struct_type in ['SumModule', 'MulModule']:
            # Verificar si ambas cintas de entrada tienen items listos
            if hasattr(struct, 'inConveyor1') and hasattr(struct, 'inConveyor2'):
                conv1 = struct.inConveyor1
                conv2 = struct.inConveyor2
                
                # Verificar que ambas cintas existen, tienen items y están listos
                if (conv1 and conv2 and 
                    hasattr(conv1, 'isReady') and hasattr(conv2, 'isReady') and
                    conv1.isReady() and conv2.isReady() and
                    hasattr(struct, 'outConveyor') and struct.outConveyor):
                    try:
                        struct.calcular()
                    except Exception as e:
                        print(f"Error in {struct_type}.calcular(): {e}")
    
    # tick and caption
    gm.delta_time = gm.clock.tick(FPS)
    # Mantener título fijo y evitar mostrar los FPS en la ventana
    try:
        pg.display.set_caption("Number Tycoon")
    except Exception:
        pass

    # Update HUD (handles popup timer centrally)
    try:
        if hasattr(gm, 'hud') and gm.hud:
            try:
                gm.hud.update(gm.delta_time)
            except Exception:
                pass
    except Exception:
        pass
