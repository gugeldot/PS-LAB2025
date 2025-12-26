from gameState import GameState


class BuildState(GameState):
    def __init__(self, placementController):
        self.placementController = placementController

    def handleClickEvent(self, event):
        # Delegar el manejo del evento de clic al controlador de colocación
        self.placementController.checkClickEvent(event)
    
    def update(self):
        self.placementController.update()
    
    def draw(self):
        self.placementController.draw()

    def setFactory(self, factory):
        self.placementController.setFactory(factory)