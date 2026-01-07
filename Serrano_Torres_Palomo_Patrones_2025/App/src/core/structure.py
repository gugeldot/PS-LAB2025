"""Base structure abstraction used across core modules.

Subclasses must implement :meth:`update` and :meth:`draw`. This module
defines the minimal interface consumed by the rest of the game logic.
"""

from abc import ABC, abstractmethod


class Structure(ABC):
    """Abstract base class for all placeable structures (mines, modules, etc.)."""

    @abstractmethod
    def update(self):
        """Advance internal state once per frame."""
        pass

    @abstractmethod
    def draw(self):
        """Render the structure on screen."""
        pass

    def getCost(self):
        """Return the build cost for this structure (optional).

        Subclasses may override to provide cost information used by builders.
        """
        pass

