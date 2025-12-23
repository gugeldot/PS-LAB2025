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
        self.width = 8
        self.color = (128, 128, 128)
        self.travel_time = 2000
        self.outputConveyor = None
        
    def push(self, number):
        self.queue.append({'value': number, 'position': 0.0})
        '''
        try:
            #print(f"Conveyor: pushed {number}, queue size now {len(self.queue)}")
        except Exception:
            pass '''
    
    def pop(self):
        if self.queue and self.queue[0]['position'] >= 1.0:
            val = self.queue.popleft()['value']
            '''
            try:
                #print(f"Conveyor: popped {val}, queue size now {len(self.queue)}")
            except Exception:
                pass'''
            return val
        return None
    
    def peek(self):
        if self.queue:
            return self.queue[0]['value']
        return None
    
    def isEmpty(self):
        return len(self.queue) == 0
    
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
    
    def connectOutput(self, conveyor):
        self.outputConveyor = conveyor
    
    def draw(self):
        pg.draw.line(self.gameManager.screen, self.color, 
                    (int(self.start_pos.x), int(self.start_pos.y)),
                    (int(self.end_pos.x), int(self.end_pos.y)), self.width)
        
        font = pg.font.Font(None, 22)
        for item in self.queue:
            t = item['position']
            pos_x = self.start_pos.x + (self.end_pos.x - self.start_pos.x) * t
            pos_y = self.start_pos.y + (self.end_pos.y - self.start_pos.y) * t
            
            text = font.render(str(item['value']), True, (255, 255, 0))
            text_rect = text.get_rect(center=(pos_x, pos_y))
            self.gameManager.screen.blit(text, text_rect)
