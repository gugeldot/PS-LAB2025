import pygame as pg
import pathlib
from settings import WIDTH, HEIGHT
try:
    from PIL import Image, ImageSequence
except Exception:
    Image = None

# Paleta de colores pastel minimalista
class Colors:
    # Backgrounds
    BG_DARK = (45, 52, 64)  # Azul oscuro profundo (ventana)
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
    # Submenu/buttons accent (más llamativo que gris)
    SUBMENU_BUTTON = (52, 152, 219)      # azul vivo
    SUBMENU_HOVER = (41, 128, 185)       # azul oscuro al pasar el ratón
    SUBMENU_TEXT = (255, 255, 255)       # texto claro sobre boton


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
        # GIF modal (se muestra al iniciar nueva partida)
        self.gif_modal_active = False
        self.gif_files = []
        self.gif_index = 0
        self.gif_frames = []  # list of Surfaces for current gif
        self.gif_frame_durations = []  # ms per frame
        self.gif_frame_index = 0
        self.gif_frame_timer = 0
        self.gif_titles = []  # parallel list of titles for gif_files
        # modal button rects (created when modal is drawn/initialized)
        self.modal_prev_button = None
        self.modal_next_button = None
        self.modal_exit_button = None

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
            y_destroy = y_build + (self.button_height + self.button_margin) * 7  # 6 botones BUILD + 1 espacio
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
        # Nota: el módulo División ha sido eliminado de la UI (no exponerlo en HUD)
        self.splitter_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 3,
            self.button_width,
            self.button_height
        )
        self.merger_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 4,
            self.button_width,
            self.button_height
        )
        self.conveyor_button = pg.Rect(
            self.right_margin,
            y_build + (self.button_height + self.button_margin) * 5,
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
        # GIF modal animation timing
        try:
            if getattr(self, 'gif_modal_active', False):
                if not self.gif_frames:
                    return
                # Ensure integers and consistent units (delta_time is ms from pygame.Clock.tick)
                dt = int(delta_time)
                self.gif_frame_timer += dt
                # guard against malformed durations; fallback to 100ms
                try:
                    cur_dur = int(self.gif_frame_durations[self.gif_frame_index]) if self.gif_frame_durations else 100
                except Exception:
                    cur_dur = 100
                if self.gif_frame_timer >= max(1, cur_dur):
                    self.gif_frame_timer = 0
                    self.gif_frame_index = (self.gif_frame_index + 1) % len(self.gif_frames)
        except Exception:
            pass
    
    def draw(self, screen, mouse_pos):
        """Dibuja todos los elementos del HUD"""
        # Dibujar una zona semitransparente que indica "área no clickable del mapa"
        try:
            self._draw_blocked_area(screen)
        except Exception:
            pass
        self._draw_points_display(screen)
        self._draw_buttons(screen, mouse_pos)
        self._draw_popup(screen)
        # If GIF modal active, draw it last so it appears on top
        try:
            if getattr(self, 'gif_modal_active', False):
                self._draw_gif_modal(screen)
        except Exception:
            pass

    def _draw_blocked_area(self, screen):
        """Dibuja un rectángulo semitransparente sobre la franja del HUD para
        indicar que por ahí no se puede clickar el mapa (evita clicks 'pasantes').
        Se dibuja detrás de los botones para no interferir visualmente.
        """
        try:
            # Mantener la posición izquierda (no moverla) pero extender
            # el rectángulo hasta el borde derecho de la pantalla.
            strip_x = max(0, self.right_margin - 8)
            strip_w = WIDTH - strip_x
            s = pg.Surface((strip_w, HEIGHT), pg.SRCALPHA)
            # color oscuro con baja opacidad
            s.fill((0, 0, 0, 80))
            screen.blit(s, (strip_x, 0))
        except Exception:
            pass
    
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
                        # Use original/base consumingNumber if available so the
                        # HUD shows the intended next objective even after
                        # efficiency upgrades have increased runtime values.
                        def _base_consuming(w):
                            try:
                                return int(getattr(w, '_base_consumingNumber', getattr(w, 'consumingNumber', float('inf'))))
                            except Exception:
                                return float('inf')

                        min_num = min(_base_consuming(w) for w in locked_wells)
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
            # treat None as unlimited
            speed_remaining = getattr(self.game, 'speed_uses_left', None)
            can_buy_speed = (self.game.points >= (next_speed_cost or 0)) and (speed_remaining is None or speed_remaining > 0)

            # Show remaining uses in parentheses and cost below
            rem_display = str(speed_remaining) if speed_remaining is not None else "∞"
            label = f"Velocidad ({rem_display})"
            sublabel = f"Coste: {next_speed_cost}"
            self._draw_button(
                screen,
                self.speed_button,
                label,
                mouse_pos,
                can_use=can_buy_speed,
                accent=True,
                sublabel=sublabel
            )
            
            # Efficiency Upgrade Button
            next_eff_cost = self._get_next_cost(self.game.eff_costs, self.game.eff_uses_used)
            eff_remaining = getattr(self.game, 'eff_uses_left', None)
            can_buy_eff = (self.game.points >= (next_eff_cost or 0)) and (eff_remaining is None or eff_remaining > 0)

            rem_display = str(eff_remaining) if eff_remaining is not None else "∞"
            label = f"Eficiencia ({rem_display})"
            sublabel = f"Coste: {next_eff_cost}"
            self._draw_button(
                screen,
                self.efficiency_button,
                label,
                mouse_pos,
                can_use=can_buy_eff,
                accent=True,
                sublabel=sublabel
            )
            
            # New Mine Button
            # determine mine cost: if index exceeds defined list, use last value
            try:
                idx = int(getattr(self.game, 'mine_uses_used', 0))
                if getattr(self.game, 'mine_costs', None) and len(self.game.mine_costs) > 0:
                    if 0 <= idx < len(self.game.mine_costs):
                        next_mine_cost = int(self.game.mine_costs[idx])
                    else:
                        next_mine_cost = int(self.game.mine_costs[-1])
                else:
                    next_mine_cost = None
            except Exception:
                next_mine_cost = None

            can_buy_mine = (self.game.points >= (next_mine_cost or 0))

            mine_remaining = getattr(self.game, 'mine_uses_left', None)
            rem_display = str(mine_remaining) if mine_remaining is not None else "∞"
            label = f"Nueva Mina"
            sublabel = f"Coste: {next_mine_cost}"
            self._draw_button(
                screen,
                self.new_mine_button,
                label,
                mouse_pos,
                can_use=can_buy_mine,
                accent=True,
                sublabel=sublabel
            )
        elif self.shop_mode=="BUILD":
            #si esta en modo construccion se dibujan las opciones de modulos
            # obtener costes desde gm.build_costs (fallback a 15)
            try:
                costs = getattr(self.game, 'build_costs', {}) or {}
            except Exception:
                costs = {}

            sum_cost = int(costs.get('sum', 15))
            mul_cost = int(costs.get('mul', 25))
            splitter_cost = int(costs.get('splitter', 20))
            merger_cost = int(costs.get('merger', 20))

            can_buy_sum = getattr(self.game, 'points', 0) >= sum_cost
            can_buy_mul = getattr(self.game, 'points', 0) >= mul_cost
            can_buy_splitter = getattr(self.game, 'points', 0) >= splitter_cost
            can_buy_merger = getattr(self.game, 'points', 0) >= merger_cost
            self._draw_button(
                screen,
                self.sum_module_button,
                f"Módulo Suma",
                mouse_pos,
                can_use=can_buy_sum,
                accent=True,
                sublabel=f"Coste: {sum_cost}"
            )
            self._draw_button(
                screen,
                self.mul_module_button,
                f"Módulo Multiplicación",
                mouse_pos,
                can_use=can_buy_mul,
                accent=True,
                sublabel=f"Coste: {mul_cost}"
            )
            self._draw_button(
                screen,
                self.splitter_button,
                f"Splitter",
                mouse_pos,
                can_use=can_buy_splitter,
                accent=True,
                sublabel=f"Coste: {splitter_cost}"
            )
            self._draw_button(
                screen,
                self.merger_button,
                f"Merger",
                mouse_pos,
                can_use=can_buy_merger,
                accent=True,
                sublabel=f"Coste: {merger_cost}"
            )
            
            # Botón de cintas transportadoras: leer coste desde `gm.build_costs`
            try:
                costs = getattr(self.game, 'build_costs', {}) or {}
            except Exception:
                costs = {}
            conveyor_cost = int(costs.get('conveyor', 5))
            can_buy_conveyor = getattr(self.game, 'points', 0) >= conveyor_cost
            self._draw_button(
                screen,
                self.conveyor_button,
                f"Cinta Transportadora",
                mouse_pos,
                can_use=can_buy_conveyor,
                accent=True,
                sublabel=f"Coste: {conveyor_cost}"
            )
            

            
    
    def _draw_button(self, screen, rect, label, mouse_pos, can_use=True, sublabel=None, accent=False, special_style=False):
        """Dibuja un botón individual con estilo minimalista"""
        is_hover = rect.collidepoint(mouse_pos)
        
        # Determinar color
        if not can_use:
            color = Colors.BUTTON_DISABLED
            text_color = Colors.TEXT_SECONDARY
        elif accent:
            # Estilo destacado para opciones de submenú (shop/build)
            color = Colors.SUBMENU_HOVER if is_hover else Colors.SUBMENU_BUTTON
            text_color = Colors.SUBMENU_TEXT
        elif is_hover:
            color = Colors.BUTTON_HOVER
            text_color = Colors.TEXT_PRIMARY
        else:
            color = Colors.BUTTON_DEFAULT
            text_color = Colors.TEXT_PRIMARY

        if special_style:
            # special_style tiene prioridad (botones principales)
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
            sublabel_color = Colors.SUBMENU_TEXT if accent else Colors.TEXT_SECONDARY
            sublabel_surf = pg.font.Font(None, 18).render(sublabel, True, sublabel_color)
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

    # ---------------- GIF modal support ----------------
    def open_gif_modal(self, start_index: int = 0):
        """Abre el modal de GIFs leyendo Assets/gifs. start_index permite
        iniciar en un GIF concreto."""
        try:
            base = pathlib.Path(__file__).resolve().parents[2]
            gif_dir = base / "Assets" / "gifs"
            if not gif_dir.exists() or not gif_dir.is_dir():
                self.gif_files = []
                return
            # If GameManager provides an explicit order tuple, use it to
            # build the file list in that order. Otherwise enumerate files.
            order = None
            try:
                order = getattr(self.game, 'gifs_order', None)
            except Exception:
                order = None

            files = []
            titles = []
            if order and isinstance(order, (list, tuple)) and len(order) > 0:
                for entry in order:
                    try:
                        # entry can be a string (filename) or a (filename, title) pair
                        if isinstance(entry, (list, tuple)) and len(entry) >= 1:
                            fname = str(entry[0])
                            title = str(entry[1]) if len(entry) >= 2 else None
                        else:
                            fname = str(entry)
                            title = None
                        p = gif_dir / fname
                        if p.exists() and p.is_file():
                            files.append(p)
                            titles.append(title if title is not None else p.stem)
                    except Exception:
                        pass
            # fallback: scan directory alphabetically
            if not files:
                scanned = sorted([p for p in gif_dir.iterdir() if p.suffix.lower() in ('.gif',)])
                files = scanned
                titles = [p.stem for p in scanned]
            if not files:
                self.gif_files = []
                self.gif_titles = []
                return
            self.gif_files = files
            self.gif_titles = titles
            self.gif_index = max(0, min(start_index, len(self.gif_files) - 1))
            self._load_current_gif_frames()
            self.gif_modal_active = True
            self.gif_frame_index = 0
            self.gif_frame_timer = 0
            # Pause game simulation while tutorial modal is open so nothing
            # progresses in the background (production, conveyors, etc.).
            try:
                if hasattr(self, 'game') and self.game is not None:
                    setattr(self.game, '_tutorial_paused', True)
            except Exception:
                pass
        except Exception:
            self.gif_files = []
            self.gif_modal_active = False

    def close_gif_modal(self):
        try:
            self.gif_modal_active = False
            self.gif_files = []
            self.gif_frames = []
            self.gif_frame_durations = []
            self.modal_prev_button = None
            self.modal_next_button = None
            self.modal_exit_button = None
            # Resume game simulation when closing the tutorial modal
            try:
                if hasattr(self, 'game') and self.game is not None:
                    setattr(self.game, '_tutorial_paused', False)
            except Exception:
                pass
        except Exception:
            pass

    def next_gif(self):
        try:
            if not self.gif_files:
                return
            self.gif_index = (self.gif_index + 1) % len(self.gif_files)
            self._load_current_gif_frames()
            self.gif_frame_index = 0
            self.gif_frame_timer = 0
        except Exception:
            pass

    def prev_gif(self):
        try:
            if not self.gif_files:
                return
            self.gif_index = (self.gif_index - 1) % len(self.gif_files)
            self._load_current_gif_frames()
            self.gif_frame_index = 0
            self.gif_frame_timer = 0
        except Exception:
            pass

    def _load_current_gif_frames(self):
        """Carga los frames del GIF actual en self.gif_frames y durations.
        Usa Pillow si está disponible, si no, carga una sola imagen con pygame."""
        self.gif_frames = []
        self.gif_frame_durations = []
        try:
            path = self.gif_files[self.gif_index]
        except Exception:
            return
        # Try PIL for animated GIFs (use ImageSequence for robustness)
        if Image is None:
            # Pillow not installed: fall back to pygame single-frame loading
            pass
        else:
            try:
                from PIL import ImageSequence
                img = Image.open(str(path))
                frames = []
                durations = []
                for frame in ImageSequence.Iterator(img):
                    try:
                        f = frame.convert('RGBA')
                        data = f.tobytes()
                        size = f.size
                        try:
                            surf = pg.image.fromstring(data, size, 'RGBA')
                        except Exception:
                            surf = pg.Surface(size, pg.SRCALPHA)
                        dur = frame.info.get('duration', img.info.get('duration', 100))
                        try:
                            dur = int(dur)
                        except Exception:
                            dur = 100
                        frames.append(surf)
                        durations.append(dur)
                    except Exception:
                        # skip problematic frames
                        continue

                if frames:
                    self.gif_frames = frames
                    self.gif_frame_durations = durations
                    return
            except Exception as e:
                # Pillow attempted to load but failed; fallback to pygame below.
                pass

        # Fallback: single-frame via pygame
        try:
            s = pg.image.load(str(path)).convert_alpha()
            self.gif_frames = [s]
            self.gif_frame_durations = [2000]
        except Exception:
            self.gif_frames = []
            self.gif_frame_durations = []

    def _draw_gif_modal(self, screen):
        """Dibuja el modal central con el frame actual y los botones."""
        if not getattr(self, 'gif_modal_active', False) or not self.gif_frames:
            return
        try:
            # semi-transparent backdrop
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            # current frame
            frame = self.gif_frames[self.gif_frame_index]
            # scale to fit 70% of screen
            max_w = int(WIDTH * 0.7)
            max_h = int(HEIGHT * 0.7)
            fw, fh = frame.get_size()
            scale = min(1.0, max_w / fw if fw else 1.0, max_h / fh if fh else 1.0)
            if scale != 1.0:
                frame_to_draw = pg.transform.smoothscale(frame, (int(fw * scale), int(fh * scale)))
            else:
                frame_to_draw = frame

            modal_w, modal_h = frame_to_draw.get_size()
            padding = 18
            # determine title (if provided) and its height
            title_text = None
            try:
                if getattr(self, 'gif_titles', None):
                    title_text = self.gif_titles[self.gif_index]
            except Exception:
                title_text = None
            title_height = 0
            title_surf = None
            if title_text:
                try:
                    title_surf = self.font_medium.render(str(title_text), True, Colors.TEXT_PRIMARY)
                    title_height = title_surf.get_height() + 6
                except Exception:
                    title_surf = None
                    title_height = 0

            total_w = modal_w + padding * 2
            total_h = modal_h + padding * 3 + 40 + title_height  # extra for title and buttons area
            x = (WIDTH - total_w) // 2
            y = (HEIGHT - total_h) // 2

            # background
            bg_rect = pg.Rect(x, y, total_w, total_h)
            self._draw_rounded_rect(screen, bg_rect, Colors.BG_LIGHT, 12)
            self._draw_rounded_rect(screen, bg_rect, Colors.BUTTON_HOVER, 12, 2)

            # draw title (if any) and then blit frame below it
            img_x = x + padding
            img_y = y + padding
            if title_surf:
                try:
                    title_x = x + (total_w - title_surf.get_width()) // 2
                    title_y = y + 8
                    screen.blit(title_surf, (title_x, title_y))
                    img_y = title_y + title_surf.get_height() + 6
                except Exception:
                    img_y = y + padding

            screen.blit(frame_to_draw, (img_x, img_y))

            # buttons: <  Exit  >  (wider spacing, smaller side buttons)
            side_w = 60
            exit_w = 120
            btn_h = 40
            spacing = 36
            btn_y = y + padding + modal_h + 12 + title_height
            center_x = x + total_w // 2

            self.modal_prev_button = pg.Rect(center_x - side_w - spacing - exit_w // 2, btn_y, side_w, btn_h)
            self.modal_exit_button = pg.Rect(center_x - exit_w // 2, btn_y, exit_w, btn_h)
            self.modal_next_button = pg.Rect(center_x + spacing + exit_w // 2, btn_y, side_w, btn_h)

            self._draw_button(screen, self.modal_prev_button, "<", pg.mouse.get_pos(), can_use=True)
            self._draw_button(screen, self.modal_exit_button, "Salir", pg.mouse.get_pos(), can_use=True)
            self._draw_button(screen, self.modal_next_button, ">", pg.mouse.get_pos(), can_use=True)

            # caption showing (index/total)
            try:
                total = len(self.gif_files)
                caption = f"({self.gif_index + 1}/{total})"
                cap = self.font_small.render(caption, True, Colors.TEXT_PRIMARY)
                cap_x = x + (total_w - cap.get_width()) // 2
                cap_y = y + total_h - cap.get_height() - 6
                screen.blit(cap, (cap_x, cap_y))
            except Exception:
                pass
        except Exception:
            pass
    
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

        # If the GIF modal is active, block all interactions behind it.
        # This prevents any clicks on buttons, cells or map elements while
        # the tutorial/modal is displayed.
        try:
            if getattr(self, 'gif_modal_active', False):
                return True
        except Exception:
            pass

        # Antes de comprobar botones individuales, si la posición está dentro
        # de la franja del HUD (la columna derecha) consideramos que está sobre
        # la UI para evitar clicks que "pasen" entre botones.
        try:
            strip_x = max(0, self.right_margin - 8)
            hud_strip = pg.Rect(strip_x, 0, WIDTH - strip_x, HEIGHT)
            if hud_strip.collidepoint(pos):
                return True
        except Exception:
            pass

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
            getattr(self, 'splitter_button', None),
            getattr(self, 'merger_button', None),
            getattr(self, 'conveyor_button', None),
            getattr(self, 'destroy_button', None),
        ]

        # include modal buttons to block clicks to map when modal open
        try:
            if getattr(self, 'gif_modal_active', False):
                rects.append(getattr(self, 'modal_prev_button', None))
                rects.append(getattr(self, 'modal_next_button', None))
                rects.append(getattr(self, 'modal_exit_button', None))
        except Exception:
            pass

        for r in rects:
            if r and r.collidepoint(pos):
                return True

        return False

