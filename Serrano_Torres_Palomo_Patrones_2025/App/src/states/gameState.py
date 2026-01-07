"""Base class for game states.

`GameState` defines the minimal interface used by the game's state
machine: handleClickEvent, update and draw. Concrete states implement
these methods and are used to switch the game's behavior (build, destroy,
normal, etc.).
"""


class GameState:
    def handleClickEvent(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass