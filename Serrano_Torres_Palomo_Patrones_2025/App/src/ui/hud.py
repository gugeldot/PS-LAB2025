import pygame as pg
from settings import WIDTH, HEIGHT

# Paleta de colores pastel minimalista
class Colors:
    # Backgrounds
    BG_DARK = (45, 52, 64)  # Azul oscuro suave
    BG_LIGHT = (236, 240, 241)  # Gris muy claro
    
    # UI Elements
    BUTTON_DEFAULT = (178, 190, 195)  # Gris azulado pastel
    BUTTON_HOVER = (149, 175, 192)  # Azul pastel
    BUTTON_DISABLED = (127, 140, 141)  # Gris oscuro apagado
    BUTTON_ACTIVE = (130, 204, 221)  # Azul claro vibrante
    
    # Text
    TEXT_PRIMARY = (44, 62, 80)  # Azul oscuro para texto principal
    TEXT_SECONDARY = (149, 165, 166)  # Gris para texto secundario
    TEXT_LIGHT = (236, 240, 241)  # Texto claro para fondos oscuros
    TEXT_ACCENT = (255, 234, 167)  # Amarillo suave para puntos
    
    # Structures (colores pastel)
    MINE = (255, 177, 193)  # Rosa pastel
    WELL = (163, 228, 215)  # Verde menta pastel
    CONVEYOR = (189, 195, 199)  # Gris plateado
    SPLITTER = (174, 214, 241)  # Azul cielo pastel
    MERGER = (210, 180, 222)  # Lavanda pastel
    OPERATOR = (255, 218, 185)  # Melocotón pastel
    
    # Grid
    GRID_LINE = (55, 65, 75)  # Gris muy oscuro, casi imperceptible
    GRID_HOVER = (149, 175, 192, 100)  # Azul transparente para hover
    
    # Accents
    SUCCESS = (129, 236, 236)  # Cyan pastel
    WARNING = (253, 203, 110)  # Amarillo pastel
    ERROR = (255, 159, 163)  # Rojo coral pastel


class HUD:
    def __init__(self, game_manager):
        self.game = game_manager
        
        # Fonts
        self.font_large = pg.font.Font(None, 40)
        self.font_medium = pg.font.Font(None, 28)
        self.font_small = pg.font.Font(None, 22)
        
        # Button dimensions y padding
        self.button_width = 180
        self.button_height = 45
        self.button_padding = 12
        self.button_margin = 10
        
        # Posiciones de botones (alineados a la derecha con margen)
        self.right_margin = WIDTH - self.button_width - 15
        
        # para tienda de mejoras
        self.shop_open = False
        self.shop_mode = None  # Puede ser: None, "SHOP","BUILD" o "DESTROY"

        # Definir rectángulos de botones
        self._setup_buttons()

        # Nota: el popup global se gestiona en el GameManager a través de
        # `_popup_message` y `_popup_timer`. Este HUD delega el temporizado
        # allí para evitar duplicidad y asegurar que un único contador rige.
        self.popup_duration = 3000  # ms (valor por defecto usado si se llama show_popup)
        # Mantener atributos locales para compatibilidad con código antiguo
        # que esperaba `hud.popup_message`/`hud.popup_timer`.
        self.popup_message = None
        self.popup_timer = 0
        

    def _setup_buttons(self):
        """Configura las posiciones de todos los botones del HUD"""
        y_start = 15
        up_pos = y_start + (self.button_height + self.button_margin) * 1
        bot_pos = y_start + (self.button_height + self.button_margin) * 5

        if self.shop_mode == "SHOP":
            y_shop = up_pos
            y_build = bot_pos
            y_destroy = y_build + (self.button_height + self.button_margin) * 1
        elif self.shop_mode == "BUILD":
            y_shop = up_pos
            y_build = up_pos + (self.button_height + self.button_margin)
            y_destroy = y_build + (self.button_height + self.button_margin) * 4
        else:
            y_shop = up_pos
            y_build = up_pos + (self.button_height + self.button_margin)
            y_destroy = y_build + (self.button_height + self.button_margin) * 1

        self.save_button = pg.Rect(
            self.right_margin, 
            y_start  ,
            self.button_width, 
            self.button_height
        )

        self.shop_button = pg.Rect(
            self.right_margin, 
            y_shop,
            self.button_width, 
            self.button_height
            )
        self.build_button = pg.Rect(
            self.right_margin,
            y_build,
            self.button_width,
            self.button_height
        )
        self.speed_button = pg.Rect(
            self.right_margin,
            y_start + (self.button_height + self.button_margin) * 2,
            self.button_width,
            self.button_height
        )
        
        self.efficiency_button = pg.Rect(
            self.right_margin,
            y_start + (self.button_height + self.button_margin) * 3,
            self.button_width,
            self.button_height
        )
        
        self.new_mine_button = pg.Rect(
            self.right_margin,
            y_start + (self.button_height + self.button_margin) * 4,
            self.button_width,
            self.button_height
        )

        self.sum_module_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 1,
            self.button_width,
            self.button_height
        )
        self.mul_module_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 2,
            self.button_width,
            self.button_height
        )
        self.div_module_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 3,
            self.button_width,
            self.button_height
        )
        self.destroy_button = pg.Rect(
            self.right_margin,
            y_destroy,
            self.button_width,
            self.button_height
        )
        
    
    def show_popup(self, message, duration=None):
        """Request a popup message. Prefer to write into the GameManager
        so a single timer is used for all popups. If no GameManager is
        attached, the HUD will set the internal values (fallback).

        Also suppress the specific annoying message "Botón activado".
        """
        # Suprimir el popup molesto de "Botón activado"
        try:
            if isinstance(message, str) and "botón activ" in message.lower():
                return
        except Exception:
            pass

        dur = int(duration if duration is not None else self.popup_duration)
        try:
            # Preferir escribir el popup en el GameManager para que el
            # temporizador sea gestionado desde gm.update
            if hasattr(self, 'game') and self.game is not None:
                try:
                    self.game._popup_message = str(message)
                    self.game._popup_timer = dur
                    return
                except Exception:
                    pass
        except Exception:
            pass

        # Fallback: mantener atributos locales (no debería ocurrir en práctica)
        self.popup_message = str(message)
        self.popup_timer = dur
    
    def update(self, delta_time):
        """Actualiza el estado del HUD"""
        # Delegar el temporizado de popups al GameManager: decrementar
        # `_popup_timer` si existe. Esto asegura una única fuente de verdad
        # para el mensaje temporal.
        try:
            if hasattr(self.game, '_popup_timer') and getattr(self.game, '_popup_timer', None) is not None:
                try:
                    self.game._popup_timer -= int(delta_time)
                except Exception:
                    try:
                        self.game._popup_timer -= 0
                    except Exception:
                        pass
                if self.game._popup_timer <= 0:
                    try:
                        self.game._popup_timer = None
                        self.game._popup_message = None
                    except Exception:
                        pass
        except Exception:
            # Fallback local decrement (very rare)
            try:
                if getattr(self, 'popup_timer', 0) > 0:
                    self.popup_timer -= int(delta_time)
                    if self.popup_timer <= 0:
                        self.popup_timer = 0
                        self.popup_message = None
            except Exception:
                pass
    
    def draw(self, screen, mouse_pos):
        """Dibuja todos los elementos del HUD"""
        self._draw_points_display(screen)
        self._draw_buttons(screen, mouse_pos)
        self._draw_popup(screen)
    
    def _draw_points_display(self, screen):
        """Dibuja el contador de puntos con estilo minimalista"""
        points = getattr(self.game, 'points', 0)
        
        # Fondo con bordes redondeados
        padding = 16
        text_surf = self.font_large.render(f"{points}", True, Colors.TEXT_ACCENT)
        label_surf = self.font_small.render("PUNTOS", True, Colors.TEXT_SECONDARY)

        # determinar objetivo siguiente basándonos en el número del pozo
        # (consumingNumber). Esto asegura que el siguiente objetivo mostrado
        # corresponde al siguiente pozo numérico bloqueado (1->2->3...).
        next_obj = None
        try:
            wells = getattr(self.game, 'wells', None)
            objectives = getattr(self.game, 'well_objectives', None)
            if wells and objectives:
                locked_wells = [w for w in wells if getattr(w, 'locked', False)]
                if locked_wells:
                    try:
                        min_num = min(int(getattr(w, 'consumingNumber', float('inf'))) for w in locked_wells)
                        idx = int(min_num) - 1
                        if 0 <= idx < len(objectives):
                            next_obj = int(objectives[idx])
                    except Exception:
                        next_obj = None
        except Exception:
            next_obj = None

        if next_obj is not None:
            objective_surf = self.font_small.render(f"Nuevo Objetivo: {next_obj} puntos", True, Colors.TEXT_SECONDARY)
        else:
            objective_surf = None

        total_width = max(text_surf.get_width(), label_surf.get_width(), (objective_surf.get_width() if objective_surf else 0)) + padding * 2
        total_height = text_surf.get_height() + label_surf.get_height() + (objective_surf.get_height() if objective_surf else 0) + padding * 2
        
        x = 15
        y = HEIGHT - total_height - 15
        
        # Fondo redondeado
        bg_rect = pg.Rect(x, y, total_width, total_height)
        self._draw_rounded_rect(screen, bg_rect, Colors.BG_DARK, 12)
        
        # Borde sutil
        self._draw_rounded_rect(screen, bg_rect, Colors.BUTTON_HOVER, 12, 2)
        
        # Texto de puntos (centrado)
        text_x = x + (total_width - text_surf.get_width()) // 2
        text_y = y + padding
        screen.blit(text_surf, (text_x, text_y))
        
        # Label "PUNTOS"
        label_x = x + (total_width - label_surf.get_width()) // 2
        label_y = text_y + text_surf.get_height() + 4
        screen.blit(label_surf, (label_x, label_y))
        # Objetivo siguiente (si existe)
        if objective_surf:
            obj_x = x + (total_width - objective_surf.get_width()) // 2
            obj_y = label_y + label_surf.get_height() + 2
            screen.blit(objective_surf, (obj_x, obj_y))
    
    def _draw_buttons(self, screen, mouse_pos):
        """Dibuja todos los botones del HUD"""

        # Save Button
        self._draw_button(
            screen, 
            self.save_button, 
            "GUARDAR Y SALIR",
            mouse_pos,
            can_use=True,
            special_style=True
            )
        
        shop_text = "CERRAR TIENDA" if self.shop_mode=="SHOP" else "ABRIR TIENDA"
        #shop button
        self._draw_button(
            screen, 
            self.shop_button, 
            shop_text, 
            mouse_pos, 
            special_style=not self.shop_mode=="SHOP")
        
        self._draw_button(
                screen, 
                self.build_button, 
                "MODO CONSTRUCCIÓN", 
                mouse_pos, 
                special_style=True)
        
        self._draw_button(
                screen,
                self.destroy_button,
                "MODO DESTRUCCIÓN",
                mouse_pos,
                special_style=True)
        
        
        if self.shop_mode=="SHOP":
            #si esta modo tienda se dibujan las opciones de compra
            # Speed Upgrade Button
            next_speed_cost = self._get_next_cost(self.game.speed_costs, self.game.speed_uses_used)
            can_buy_speed = (self.game.points >= (next_speed_cost or 0)) and (self.game.speed_uses_left > 0)
            
            label = f"Velocidad ({next_speed_cost})"
            sublabel = f"Quedan: {self.game.speed_uses_left}"
            self._draw_button(
                screen,
                self.speed_button,
                label,
                mouse_pos,
                can_use=can_buy_speed,
                sublabel=sublabel
            )
            
            # Efficiency Upgrade Button
            next_eff_cost = self._get_next_cost(self.game.eff_costs, self.game.eff_uses_used)
            can_buy_eff = (self.game.points >= (next_eff_cost or 0)) and (self.game.eff_uses_left > 0)
            
            label = f"Eficiencia ({next_eff_cost})"
            sublabel = f"Quedan: {self.game.eff_uses_left}"
            self._draw_button(
                screen,
                self.efficiency_button,
                label,
                mouse_pos,
                can_use=can_buy_eff,
                sublabel=sublabel
            )
            
            # New Mine Button
            next_mine_cost = self._get_next_cost(self.game.mine_costs, self.game.mine_uses_used)
            can_buy_mine = (self.game.points >= (next_mine_cost or 0)) and (self.game.mine_uses_left > 0)
            
            label = f"Nueva Mina ({next_mine_cost})"
            sublabel = f"Quedan: {self.game.mine_uses_left}"
            self._draw_button(
                screen,
                self.new_mine_button,
                label,
                mouse_pos,
                can_use=can_buy_mine,
                sublabel=sublabel
            )
        elif self.shop_mode=="BUILD":
            #si esta en modo construccion se dibujan las opciones de modulos
            self._draw_button(
                screen,
                self.sum_module_button,
                "Módulo Suma",
                mouse_pos
            )
            self._draw_button(
                screen,
                self.mul_module_button,
                "Módulo Multiplicación",
                mouse_pos
            )
            self._draw_button(
                screen,
                self.div_module_button,
                "Módulo División",
                mouse_pos
            )
            

            
    
    def _draw_button(self, screen, rect, label, mouse_pos, can_use=True, sublabel=None, special_style=False):
        """Dibuja un botón individual con estilo minimalista"""
        is_hover = rect.collidepoint(mouse_pos)
        
        # Determinar color
        if not can_use:
            color = Colors.BUTTON_DISABLED
            text_color = Colors.TEXT_SECONDARY
        elif is_hover:
            color = Colors.BUTTON_HOVER
            text_color = Colors.TEXT_PRIMARY
        else:
            color = Colors.BUTTON_DEFAULT
            text_color = Colors.TEXT_PRIMARY
        
        if special_style:
            color = Colors.WARNING if is_hover else Colors.BUTTON_ACTIVE
            text_color = Colors.TEXT_PRIMARY
        
        # Dibujar fondo con bordes redondeados
        self._draw_rounded_rect(screen, rect, color, 10)
        
        # Efecto sutil de elevación en hover
        if is_hover and can_use:
            shadow_rect = rect.copy()
            shadow_rect.y += 2
            self._draw_rounded_rect(screen, shadow_rect, (0, 0, 0, 30), 10)
        
        # Texto principal
        text_surf = self.font_small.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery - (5 if sublabel else 0)))
        screen.blit(text_surf, text_rect)
        
        # Sublabel (información adicional)
        if sublabel:
            sublabel_surf = pg.font.Font(None, 18).render(sublabel, True, Colors.TEXT_SECONDARY)
            sublabel_rect = sublabel_surf.get_rect(center=(rect.centerx, rect.centery + 12))
            screen.blit(sublabel_surf, sublabel_rect)
    
    def _draw_popup(self, screen):
        """Dibuja el mensaje popup temporal"""
        # Preferir el popup del HUD; si no existe, comprobar si el GameManager
        # tiene un popup temporal (`_popup_message` / `_popup_timer`) y usarlo.
        msg = None
        timer = 0
        if self.popup_message and self.popup_timer > 0:
            msg = self.popup_message
            timer = self.popup_timer
        else:
            try:
                gm_msg = getattr(self.game, '_popup_message', None)
                gm_timer = int(getattr(self.game, '_popup_timer', 0) or 0)
                if gm_msg and gm_timer > 0:
                    msg = gm_msg
                    timer = gm_timer
            except Exception:
                msg = None

        if not msg or timer <= 0:
            return

        # Calcular alpha para fade out (últimos 500ms hacen fade)
        alpha = min(255, int((timer / 500) * 255))

        text_surf = self.font_medium.render(str(msg), True, Colors.TEXT_PRIMARY)
        padding = 20

        width = text_surf.get_width() + padding * 2
        height = text_surf.get_height() + padding * 2

        x = (WIDTH - width) // 2
        y = 60
        
        popup_rect = pg.Rect(x, y, width, height)
        
        # Fondo con transparencia
        bg_surface = pg.Surface((width, height))
        bg_surface.set_alpha(alpha)
        bg_surface.fill(Colors.SUCCESS)
        screen.blit(bg_surface, (x, y))
        
        # Borde (sin esquinas redondeadas)
        pg.draw.rect(screen, Colors.BUTTON_HOVER, popup_rect, 2)

        # Texto
        text_x = x + (width - text_surf.get_width()) // 2
        text_y = y + (height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
    
    def _draw_rounded_rect(self, surface, rect, color, radius, border=0):
        """Dibuja un rectángulo con bordes redondeados"""
        if border > 0:
            pg.draw.rect(surface, color, rect, border, border_radius=radius)
        else:
            pg.draw.rect(surface, color, rect, border_radius=radius)
    
    def _get_next_cost(self, cost_tuple, uses_used):
        """Obtiene el costo de la siguiente mejora"""
        try:
            if 0 <= uses_used < len(cost_tuple):
                return int(cost_tuple[uses_used])
        except:
            pass
        return None

    def is_over_button(self, pos):
        """Devuelve True si la posición de pantalla `pos` está sobre algún botón del HUD.

        `pos` debe ser una tupla (x, y) en coordenadas de pantalla (igual que event.pos).
        Esto se usa para evitar que clicks sobre la UI "pasen" al mapa debajo.
        """
        try:
            x, y = pos
        except Exception:
            return False

        # Lista de rects potenciales; algunos pueden no existir dependiendo del modo, por eso usamos getattr con default None
        rects = [
            getattr(self, 'save_button', None),
            getattr(self, 'shop_button', None),
            getattr(self, 'build_button', None),
            getattr(self, 'speed_button', None),
            getattr(self, 'efficiency_button', None),
            getattr(self, 'new_mine_button', None),
            getattr(self, 'sum_module_button', None),
            getattr(self, 'mul_module_button', None),
            getattr(self, 'div_module_button', None),
            getattr(self, 'destroy_button', None),
        ]

        for r in rects:
            if r and r.collidepoint(pos):
                return True

        return False

