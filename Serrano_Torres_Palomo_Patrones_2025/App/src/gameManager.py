
import pygame as pg
import sys
from settings import *
from mouseControl import *
from patterns.singleton import *
from core.mine import *
from core.well import *
from core.mineCreator import *
from core.wellCreator import *
from core.mergerCreator import *
from core.splitterCreator import *
from core.conveyor import *

class GameManager(Singleton):
    _initialized = False #para el singleton
    def __init__(self):
        '''
        Esto inicializa el juego con las configuraciones de settings, se llama al inicio
        '''
        if self._initialized: #para el singleton
            return
        pg.init() #inicializa pygame
        self.screen = pg.display.set_mode(RESOLUTION) #establece resolucion de pantalla
        pg.display.set_caption("Jueguito") #nombre de la ventana

        #gestion fps
        self.clock = pg.time.Clock() 
        self.delta_time=1

        #"inicio" como tal del juego
        self.running = True
        self.new_game()

    def new_game(self):
        '''
        Inicializa los elementos del juego
        '''
        self.mouse= MouseControl(self)
        
        self.mine = MineCreator().createStructure((200,200),1,self)
        self.well = WellCreator().createStructure((400,200),1,self)
        self.conveyor = Conveyor(self.mine.position, self.well.position, self)
        
        self.structures=[self.mine, self.conveyor, self.well, 
                        MergerCreator().createStructure((300,300),self),
                        SplitterCreator().createStructure((500,500),self)]
        
        self.production_timer = 0
        self.consumption_timer = 0 

    def update(self):
        '''
        Este metodo es llamado cada frame 
        recomendacion: crear metodo update en las clases y llamarlos aqui, en unity tambien se suele hacer asi
        '''
        #update de clases
        self.mouse.update()
        
        for structure in self.structures:
            structure.update()
        
        self.production_timer += self.delta_time
        if self.production_timer > 2000:
            self.mine.produce(self.conveyor)
            self.production_timer = 0
        
        self.consumption_timer += self.delta_time
        if self.consumption_timer > 2000:
            self.well.consume(self.conveyor)
            self.consumption_timer = 0

        #pantalla
        pg.display.flip() #actualiza la pantalla
        self.delta_time=self.clock.tick(FPS) #gestion de fps
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}') #actualiza el nombre de la ventana según los fps actuales
    
    
    def draw(self):
        ''' 
        dibuja los elementos en pantalla, si no me equivo el orden importa
        recomendacion: crear metodo draw en las clases y llamarlos aqui
        '''

        self.screen.fill('black')
        for structure in self.structures:
            structure.draw()
        self.mouse.draw()

    def checkEvents(self):
        ''' chequea los eventos de pygame, tiene su propia cola de eventos, es lo que va comprobando el for de abajo'''
        for event in pg.event.get(): #el propio pygame maneja una cola de eventos, los lee uno por uno y los procesa
            self.mouse.checkClickEvent(event) #chequea si se ha clickado
            if event.type == pg.QUIT or (event.type== pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                pg.quit()
                sys.exit()

    def run(self):
        ''' Esto hace que se corra el juego'''
        while self.running:
            self.checkEvents()
            self.update()
            self.draw()