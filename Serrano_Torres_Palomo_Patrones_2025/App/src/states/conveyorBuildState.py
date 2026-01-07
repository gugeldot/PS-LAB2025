from .gameState import GameState
import pygame as pg
from settings import CELL_SIZE_PX, WIDTH, HEIGHT


class ConveyorBuildState(GameState):
    """
    Estado especial para construir cintas transportadoras.
    Requiere dos clicks: punto inicial y punto final.
    """
    
    def __init__(self, gameManager, conveyorCreator):
        self.gameManager = gameManager
        self.conveyorCreator = conveyorCreator
        self.start_pos = None  # Primera posición clickeada
        self.current_mouse_pos = None  # Posición actual del mouse para preview
        self.mouse = gameManager.mouse
    
    def handleClickEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Obtener posición del mouse en coordenadas del mundo
            cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
            world_x = int(self.mouse.position.x + cam.x)
            world_y = int(self.mouse.position.y + cam.y)
            
            # Convertir a posición de píxeles centrada en la celda
            grid_x = world_x // CELL_SIZE_PX
            grid_y = world_y // CELL_SIZE_PX
            pixel_x = grid_x * CELL_SIZE_PX + CELL_SIZE_PX // 2
            pixel_y = grid_y * CELL_SIZE_PX + CELL_SIZE_PX // 2
            click_pos = pg.Vector2(pixel_x, pixel_y)
            # If the click is not over a valid map cell, ignore it and do not allow placement
            map_obj = getattr(self.gameManager, 'map', None)
            if map_obj is None or not (0 <= grid_x < getattr(map_obj, 'width', 0) and 0 <= grid_y < getattr(map_obj, 'height', 0)):
                print(f"Click at ({grid_x},{grid_y}) is outside map bounds - ignoring placement click")
                # If we were mid-placement, cancel it to avoid inconsistent state
                if self.start_pos is not None:
                    self.start_pos = None
                return

            if self.start_pos is None:
                # Primer click: validar que no sea un pozo
                structure_at_start = self._get_structure_at_grid(grid_x, grid_y)
                if structure_at_start:
                    structure_type = structure_at_start.__class__.__name__.lower()
                    if 'well' in structure_type:
                        print("Cannot start conveyor from a Well")
                        return
                
                # Guardar posición inicial
                self.start_pos = click_pos
                self.start_grid = (grid_x, grid_y)
                print(f"Conveyor start point set at grid ({grid_x}, {grid_y})")
            else:
                # Segundo click: validar que no sea una mina
                structure_at_end = self._get_structure_at_grid(grid_x, grid_y)
                if structure_at_end:
                    structure_type = structure_at_end.__class__.__name__.lower()
                    if 'mine' in structure_type:
                        print("Cannot end conveyor at a Mine")
                        self.start_pos = None
                        return
                
                # Segundo click: crear la cinta
                end_pos = click_pos
                
                # Verificar que no sean el mismo punto
                if self.start_pos.x == end_pos.x and self.start_pos.y == end_pos.y:
                    print("Cannot create conveyor: start and end points are the same")
                    self.start_pos = None
                    return
                
                # Verificar costo: preferir el coste declarado en gm.build_costs
                try:
                    costs_map = getattr(self.gameManager, 'build_costs', {}) or {}
                    cost = int(costs_map.get('conveyor', self.conveyorCreator.getCost()))
                except Exception:
                    cost = self.conveyorCreator.getCost()
                if getattr(self.gameManager, 'points', 0) >= cost:
                    # Crear la cinta
                    conveyor = self.conveyorCreator.createStructure(
                        self.start_pos, 
                        self.gameManager, 
                        end_pos
                    )
                    
                    # Agregar a la lista de conveyors y estructuras
                    if not hasattr(self.gameManager, 'conveyors'):
                        self.gameManager.conveyors = []
                    self.gameManager.conveyors.append(conveyor)
                    
                    if not hasattr(self.gameManager, 'structures'):
                        self.gameManager.structures = []
                    self.gameManager.structures.append(conveyor)
                    
                    # Deducir el costo
                    try:
                        self.gameManager.points -= cost
                    except Exception:
                        pass
                    
                    # Establecer conexiones con estructuras
                    if hasattr(self.gameManager, '_reconnect_structures'):
                        self.gameManager._reconnect_structures()
                    
                    print(f"Conveyor built from grid ({grid_x}, {grid_y}) to previous point | Cost: {cost} pts")
                    
                    # Volver al estado normal
                    self.start_pos = None
                    # Clear HUD build mode so toggles behave correctly
                    try:
                        if hasattr(self.gameManager, 'hud') and getattr(self.gameManager, 'hud'):
                            try:
                                self.gameManager.hud.shop_mode = None
                                self.gameManager.hud._setup_buttons()
                            except Exception:
                                pass
                    except Exception:
                        pass
                    if hasattr(self.gameManager, 'normalState'):
                        self.gameManager.setState(self.gameManager.normalState)
                else:
                    print(f"Not enough points to build conveyor (need {cost}, have {getattr(self.gameManager, 'points', 0)})")
                    self.start_pos = None
        
        # ESC para cancelar
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.start_pos = None
            # Clear HUD build mode when cancelling
            try:
                if hasattr(self.gameManager, 'hud') and getattr(self.gameManager, 'hud'):
                    try:
                        self.gameManager.hud.shop_mode = None
                        self.gameManager.hud._setup_buttons()
                    except Exception:
                        pass
            except Exception:
                pass
            if hasattr(self.gameManager, 'normalState'):
                self.gameManager.setState(self.gameManager.normalState)
    
    def update(self):
        # Actualizar posición del mouse para el preview
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        world_x = int(self.mouse.position.x + cam.x)
        world_y = int(self.mouse.position.y + cam.y)
        
        grid_x = world_x // CELL_SIZE_PX
        grid_y = world_y // CELL_SIZE_PX
        pixel_x = grid_x * CELL_SIZE_PX + CELL_SIZE_PX // 2
        pixel_y = grid_y * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.current_mouse_pos = pg.Vector2(pixel_x, pixel_y)
    
    def draw(self):
        """Dibuja un preview de la cinta mientras se está construyendo"""
        # Dibujar un filtro azul semitransparente por encima del HUD (similar al modo Destroy)
        try:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            # RGBA: azul suave con alpha
            overlay.fill((60, 140, 220, 70))
            self.gameManager.screen.blit(overlay, (0, 0))
        except Exception:
            pass

        if self.start_pos and self.current_mouse_pos:
            cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
            
            # Dibujar línea preview desde start_pos hasta mouse actual
            start_screen = (
                int(self.start_pos.x - cam.x),
                int(self.start_pos.y - cam.y)
            )
            end_screen = (
                int(self.current_mouse_pos.x - cam.x),
                int(self.current_mouse_pos.y - cam.y)
            )
            
            # Línea punteada en color de preview
            color = self.conveyorCreator.getSpritePreview()
            pg.draw.line(self.gameManager.screen, color, start_screen, end_screen, 4)
            
            # Círculo en el punto de inicio
            pg.draw.circle(self.gameManager.screen, (100, 200, 100), start_screen, 8)
            
            # Círculo en la posición actual del mouse
            pg.draw.circle(self.gameManager.screen, color, end_screen, 6)
    
    def _get_structure_at_grid(self, grid_x, grid_y):
        """Obtiene la estructura en una posición de grid si existe"""
        try:
            map_obj = getattr(self.gameManager, 'map', None)
            if map_obj:
                cell = map_obj.getCell(grid_x, grid_y)
                if cell:
                    return cell.getStructure()
        except Exception as e:
            pass
        return None
