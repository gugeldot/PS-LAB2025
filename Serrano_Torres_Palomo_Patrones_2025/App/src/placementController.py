import pygame as pg

class PlacementController:
    def __init__(self, gameManager,factory):
        self.gameManager = gameManager
        self.mouse= gameManager.mouse
        self.mousePosition= self.mouse.position
        self.factory = factory  #el creator

    def setFactory(self, factory):
        self.factory = factory

    def update(self, click):
        #hacer metodo draw y dec comprobacion valido 
        

        if self.checkValidPlacement(self.mousePosition) and click:
            self.factory.create(self.mousePosition.x, self.mousePosition.y)


    def draw(self):
        #metodo basico de dibujar ciruclo
        pg.draw.circle(self.gameManager.screen, self.color, (int(self.mousePosition.x), int(self.mousePosition.y)), self.radius)
        font = pg.font.Font(None, 24)
        text = font.render(str(self.consumingNumber), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.mousePosition.x, self.mousePosition.y))
        self.gameManager.screen.blit(text, text_rect)
    
    def checkValidPlacement(self, mousePos):
        #comprobar si es valido
       if not self.mouse.has_structure:
            return True
       else:
            return False
         