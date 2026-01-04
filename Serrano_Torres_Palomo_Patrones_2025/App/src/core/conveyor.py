import pygame as pg
from collections import deque
from .structure import Structure
from patterns.iterator import FlowIterator


class Conveyor(Structure):
    '''Conveyor belt that transports numbers between structures'''
    
    def __init__(self, start_pos, end_pos, gameManager, speed=1):
        self.start_pos = pg.Vector2(start_pos)
        self.end_pos = pg.Vector2(end_pos)
        self.position = self.start_pos
        self.gameManager = gameManager
        self.speed = speed
        self.queue = deque()
        self.width = 12  # Más ancho para mejor visibilidad
        self.color = (189, 195, 199)  # Gris plateado pastel
        
        # Calcular longitud de la cinta en píxeles
        self.length = (self.end_pos - self.start_pos).length()
        
        # Velocidad constante en píxeles por segundo
        self.pixels_per_second = 100.0  # Ajustable
        
        # Calcular travel_time basado en la longitud
        if self.length > 0:
            self.travel_time = (self.length / self.pixels_per_second) * 1000  # Convertir a ms
        else:
            self.travel_time = 100  # Mínimo para cintas de longitud 0
        
        self.outputConveyor = None
        
    def push(self, number):
        self.queue.append({'value': number, 'position': 0.0})
        try:
            print(f"Conveyor: pushed {number}, queue size now {len(self.queue)}")
        except Exception:
            pass
    
    def pop(self):
        if self.queue and self.queue[0]['position'] >= 1.0:
            val = self.queue.popleft()['value']
            try:
                print(f"Conveyor: popped {val}, queue size now {len(self.queue)}")
            except Exception:
                pass
            return val
        return None
    
    def peek(self):
        if self.queue:
            return self.queue[0]['value']
        return None
    
    def isEmpty(self):
        return len(self.queue) == 0
    
    def isReady(self):
        '''Returns True if there is an item at the end of the conveyor'''
        return self.queue and self.queue[0]['position'] >= 1.0
    
    def size(self):
        return len(self.queue)
    
    def createIterator(self):
        return FlowIterator([item['value'] for item in self.queue])
    
    def update(self):
        delta = self.gameManager.delta_time / self.travel_time
        for item in self.queue:
            item['position'] += delta
            if item['position'] > 1.0:
                item['position'] = 1.0
        
        if self.queue and self.queue[0]['position'] >= 1.0 and self.outputConveyor:
            number = self.pop()
            if number is not None:
                self.outputConveyor.push(number)
    
    @property
    def output(self):
        return self.outputConveyor
    
    @output.setter
    def output(self, value):
        self.outputConveyor = value

    def connectOutput(self, conveyor):
        self.output = conveyor
    
    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        start = (int(self.start_pos.x - cam.x), int(self.start_pos.y - cam.y))
        end = (int(self.end_pos.x - cam.x), int(self.end_pos.y - cam.y))
        pg.draw.line(self.gameManager.screen, self.color, start, end, self.width)

        font = pg.font.Font(None, 20)
        for item in self.queue:
            t = item['position']
            pos_x = (self.start_pos.x + (self.end_pos.x - self.start_pos.x) * t) - cam.x
            pos_y = (self.start_pos.y + (self.end_pos.y - self.start_pos.y) * t) - cam.y
            
            # Color azul oscuro, igual que los números en minas/pozos para consistencia
            text = font.render(str(item['value']), True, (44, 62, 80))
            text_rect = text.get_rect(center=(pos_x, pos_y))
            self.gameManager.screen.blit(text, text_rect)

