import pygame as pg
import pathlib
from .structure import *
from settings import CELL_SIZE_PX


class Well(Structure):
    def __init__(self, position,  consumingNumber, gameManager):
        ''' 
        Inicializa el pozo usando coordenadas de grilla (x,y). La posición
        pixel se calcula a partir de CELL_SIZE_PX y el centro de la celda.
        '''
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.consumingNumber = consumingNumber
        self.gameManager = gameManager
        self.radius = 15
        self.color = (0, 150, 0)
        
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        COIN_PATH = BASE_DIR / "Assets" / "Sprites" / "coin.svg"
        try:
            self.coin_img = pg.image.load(str(COIN_PATH)).convert_alpha()
            self.coin_img = pg.transform.scale(self.coin_img, (20, 20))
        except:
            self.coin_img = None

        # preparar color/icono para pozo bloqueado (se dibuja un candado simple)
        self._lock_color = (120, 125, 130)
        
        # Calcular dificultad y puntos predefinidos basados en la complejidad matemática
        # Números primos son más difíciles de crear con operaciones
        # Números compuestos pequeños son más fáciles
        self.difficulty = consumingNumber
        self.points_reward = self._calculate_points_by_difficulty(consumingNumber)
        
        # Intentar cargar un sprite de candado en Assets/Sprites/lock.png o .svg
        lock_paths = [BASE_DIR / "Assets" / "Sprites" / "lock.png",
                      BASE_DIR / "Assets" / "Sprites" / "lock.svg"]
        self.lock_img = None
        for LOCK_PATH in lock_paths:
            try:
                if LOCK_PATH.exists():
                    loaded = pg.image.load(str(LOCK_PATH))
                    # some surfaces may not have alpha; convert_alpha si posible
                    try:
                        loaded = loaded.convert_alpha()
                    except Exception:
                        try:
                            loaded = loaded.convert()
                        except Exception:
                            pass
                    # escalar a tamaño relativo al radio del pozo (más consistente)
                    try:
                        size = int(self.radius * 1.5)
                        loaded = pg.transform.smoothscale(loaded, (size, size))
                    except Exception:
                        pass
                    self.lock_img = loaded
                    break
            except Exception:
                # intentar siguiente formato
                self.lock_img = None

    def update(self):
        '''
        '''
        pass
    
    def _calculate_points_by_difficulty(self, num):
        """
        Calcula puntos basados en el número + bonus por dificultad.
        - Puntos base: el número mismo
        - Bonus: ×1.2 (redondeado) si es primo (más difícil de generar)
        """
        if num <= 1:
            return num
        
        # Verificar si es primo
        def is_prime(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        # Puntos base = el número consumido
        points = num
        
        # Bonus por ser primo: multiplicar por 1.2 y redondear
        if is_prime(num):
            points = round(num * 1.2)
        
        return points
    
    def connectInput(self, conveyor):
        '''Permite que el sistema de reconexión conecte una cinta al pozo'''
        # En el caso del pozo, la cinta debe saber que su salida es el pozo
        if hasattr(conveyor, 'connectOutput'):
            conveyor.connectOutput(self)

    def push(self, number):
        '''Permite que un conveyor empuje un número directamente al pozo'''
        # Si está bloqueado, ignorar todo
        if getattr(self, 'locked', False):
            # consume attempt ignored
            return

        if number is not None and number == self.consumingNumber:
            # Usar los puntos predefinidos basados en dificultad, no el número consumido
            points = getattr(self, 'points_reward', number)
            try:
                self.gameManager.points += points
            except Exception:
                pass
            print(f"Well consumed {number}! +{points} points | Total: {getattr(self.gameManager, 'points', 0)}")
            # avisar al gameManager para comprobar si hay que desbloquear pozos
            try:
                if hasattr(self.gameManager, 'unlock_next_well_if_needed'):
                    self.gameManager.unlock_next_well_if_needed()
            except Exception:
                pass

    def consume(self, conveyor):
        number = conveyor.pop()
        if number is not None and number == self.consumingNumber:
            points = number
            # NOTE: prime-based doubling removed per request — points equal the consumed number
            self.gameManager.points += points
            print(f"Well consumed {number}! +{points} points | Total: {self.gameManager.points}")

    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
        
        font = pg.font.Font(None, 24)
        text = font.render(str(self.consumingNumber), True, (255, 255, 255))
        text_rect = text.get_rect(center=draw_pos)
        self.gameManager.screen.blit(text, text_rect)

        # Mostrar puntos predefinidos basados en dificultad
        points_value = getattr(self, 'points_reward', self.consumingNumber)

        if self.coin_img:
            coin_x = int(self.position.x - cam.x - 25)
            coin_y = int(self.position.y - cam.y - 35)
            self.gameManager.screen.blit(self.coin_img, (coin_x, coin_y))
        
        points_font = pg.font.Font(None, 20)
        points_text = points_font.render(f"+{points_value}", True, (255, 215, 0))
        points_rect = points_text.get_rect(center=(int(self.position.x - cam.x + 5), int(self.position.y - cam.y - 35)))
        self.gameManager.screen.blit(points_text, points_rect)