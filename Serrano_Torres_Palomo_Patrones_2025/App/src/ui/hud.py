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
        self.shop_mode = None  # Puede ser: None, "SHOP" o "BUILD"

        # Definir rectángulos de botones
        self._setup_buttons()
        
        # Estado del popup
        self.popup_message = None
        self.popup_timer = 0
        self.popup_duration = 2000  # ms
        

    def _setup_buttons(self):
        """Configura las posiciones de todos los botones del HUD"""
        y_start = 15
        up_pos = y_start + (self.button_height + self.button_margin) * 1
        bot_pos = y_start + (self.button_height + self.button_margin) * 5

        if self.shop_mode == "SHOP":
            y_shop = up_pos
            y_build = bot_pos
        else:
            y_shop = up_pos
            y_build = up_pos + (self.button_height + self.button_margin)

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
        
    
    def show_popup(self, message, duration=2000):
        """Muestra un mensaje temporal en pantalla"""
        self.popup_message = message
        self.popup_timer = duration
    
    def update(self, delta_time):
        """Actualiza el estado del HUD"""
        if self.popup_timer > 0:
            self.popup_timer -= delta_time
            if self.popup_timer < 0:
                self.popup_timer = 0
                self.popup_message = None
    
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
        
        total_width = max(text_surf.get_width(), label_surf.get_width()) + padding * 2
        total_height = text_surf.get_height() + label_surf.get_height() + padding * 2
        
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
        if not self.popup_message or self.popup_timer <= 0:
            return
        
        # Calcular alpha para fade out
        alpha = min(255, int((self.popup_timer / 500) * 255))
        
        text_surf = self.font_medium.render(self.popup_message, True, Colors.TEXT_PRIMARY)
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
        
        # Borde
        pg.draw.rect(screen, Colors.BUTTON_HOVER, popup_rect, 2, border_radius=10)
        
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
        """Verifica si la posición está sobre algún botón del HUD"""
        if self.shop_button.collidepoint(pos):
            return True
        
        if self.shop_open:
            return (self.save_button.collidepoint(pos) or 
                self.speed_button.collidepoint(pos) or
                self.efficiency_button.collidepoint(pos) or
                self.new_mine_button.collidepoint(pos))
        return False
