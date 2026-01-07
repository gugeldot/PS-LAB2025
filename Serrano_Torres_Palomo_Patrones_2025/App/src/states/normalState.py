"""Normal state: delegate basic input handling to mouse controller.

`NormalState` forwards click handling to a provided mouse controller
object. This keeps the game's default interaction mode simple and
delegated.
"""

from .gameState import GameState


class NormalState(GameState):
    """Default game state where normal interactions are handled."""

    def __init__(self, mouse_controller):
        self.mouse_controller = mouse_controller
    
    def handleClickEvent(self, event):
        # Delegar el manejo del evento de clic al controlador del ratón
        return self.mouse_controller.checkClickEvent(event)