from .gameState import GameState
import pygame as pg
from settings import CELL_SIZE_PX

class DestroyState(GameState):
    def __init__(self, placementController):
        self.placementController = placementController
        self.gameManager = placementController.gameManager
        self.mouse = placementController.mouse

    def handleClickEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Primero intentar destruir una cinta si el click está sobre una
            conveyor = self._get_conveyor_at_click(event.pos)
            if conveyor:
                # Si se destruye algo, volver al estado normal
                try:
                    self._destroy_conveyor(conveyor)
                    if hasattr(self, 'gameManager'):
                        # Ensure HUD mode is cleared so subsequent clicks toggle correctly
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
                except Exception:
                    pass
            else:
                # Si no hay cinta, usar el comportamiento normal para estructuras
                self.placementController.update()
                try:
                    destroyed = self.placementController.destroyStructure()
                    if destroyed and hasattr(self, 'gameManager'):
                        # Clear HUD destroy mode so toggling works on next clicks
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
                except Exception:
                    pass
    
    def update(self):
        self.placementController.update()
    
    def draw(self):
        self.placementController.drawDestroy()
    
    def _get_conveyor_at_click(self, screen_pos):
        """Determina si hay una cinta cerca del click"""
        try:
            cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
            world_x = screen_pos[0] + cam.x
            world_y = screen_pos[1] + cam.y
            click_world_pos = pg.Vector2(world_x, world_y)
            
            conveyors = getattr(self.gameManager, 'conveyors', [])
            for conv in conveyors:
                # Verificar si el click está cerca de la línea de la cinta
                if self._point_near_line(click_world_pos, conv.start_pos, conv.end_pos, threshold=20):
                    return conv
        except Exception as e:
            print(f"Error detecting conveyor at click: {e}")
        return None
    
    def _point_near_line(self, point, line_start, line_end, threshold=20):
        """Verifica si un punto está cerca de una línea"""
        try:
            # Distancia punto-línea
            line_vec = line_end - line_start
            line_len = line_vec.length()
            if line_len == 0:
                return False
            
            line_unitvec = line_vec / line_len
            point_vec = point - line_start
            proj_length = point_vec.dot(line_unitvec)
            
            # Verificar si la proyección está dentro del segmento
            if proj_length < 0 or proj_length > line_len:
                return False
            
            # Punto más cercano en la línea
            closest_point = line_start + line_unitvec * proj_length
            distance = (point - closest_point).length()
            
            return distance <= threshold
        except Exception:
            return False
    
    def _destroy_conveyor(self, conveyor):
        """Destruye una cinta y devuelve puntos"""
        try:
            conveyors = getattr(self.gameManager, 'conveyors', [])
            if conveyor in conveyors:
                conveyors.remove(conveyor)
            
            structures = getattr(self.gameManager, 'structures', [])
            if conveyor in structures:
                structures.remove(conveyor)
            
            # Devolver el coste configurado para cintas (usa gm.build_costs si existe)
            try:
                refund = int(getattr(self.gameManager, 'build_costs', {}).get('conveyor', 5))
            except Exception:
                refund = 5
            if hasattr(self.gameManager, 'addPoints'):
                self.gameManager.addPoints(refund)
            elif hasattr(self.gameManager, 'points'):
                self.gameManager.points += refund
            
            print(f"Conveyor destroyed. Refund: {refund} pts")
        except Exception as e:
            print(f"Error destroying conveyor: {e}")