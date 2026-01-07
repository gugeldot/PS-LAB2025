from .gameState import GameState


class NormalState(GameState):
    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller
    
    def handleClickEvent(self, event):
        # Delegar el manejo del evento de clic al controlador del ratón
        return self.mouse_controller.checkClickEvent(event)