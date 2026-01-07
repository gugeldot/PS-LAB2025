"""Observer pattern utilities.

Simple publish/subscribe helpers used for event notification in the
game. Provides `Subject` to manage observers and several concrete
observer implementations useful for HUD updates and debugging.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Observer(ABC):
    """Interface for observers that receive event notifications.

    Implementations should provide an `update(event_type, data)` method.
    """
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Recibe notificación de un evento
        
        Args:
            event_type: Tipo de evento ('points_changed', 'structure_built', etc.)
            data: Datos relacionados con el evento
        """
        pass


class Subject:
    """Observable subject that keeps a registry of observers.

    Observers can be attached per event type and will be notified when
    events are emitted via `notify`.
    """
    
    def __init__(self):
        self._observers: Dict[str, List[Observer]] = {}
    
    def attach(self, event_type: str, observer: Observer) -> None:
        """Suscribe un observador a un tipo de evento específico"""
        if event_type not in self._observers:
            self._observers[event_type] = []
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
    
    def detach(self, event_type: str, observer: Observer) -> None:
        """Desuscribe un observador de un tipo de evento"""
        if event_type in self._observers:
            try:
                self._observers[event_type].remove(observer)
            except ValueError:
                pass
    
    def notify(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Notifica a todos los observadores suscritos a este tipo de evento"""
        if data is None:
            data = {}
        
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                try:
                    observer.update(event_type, data)
                except Exception as e:
                    print(f"Error notifying observer: {e}")


# Observadores concretos útiles para el juego

class PointsObserver(Observer):
    """Observer that reacts to changes in player points.

    Optionally shows HUD popups for significant gains.
    """
    
    def __init__(self, hud=None):
        self.hud = hud
        self.total_points = 0
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == 'points_changed':
            points = data.get('points', 0)
            delta = data.get('delta', 0)
            self.total_points = points
            if self.hud and delta > 0:
                # Mostrar popup solo para ganancias significativas
                if delta >= 5:
                    try:
                        self.hud.show_popup(f"+{delta} puntos!", 1500)
                    except:
                        pass


class StructureObserver(Observer):
    """Observer that logs structure construction and destruction events."""
    
    def __init__(self):
        self.structures_built = 0
        self.structures_destroyed = 0
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == 'structure_built':
            self.structures_built += 1
            struct_type = data.get('type', 'Unknown')
            print(f"📦 Structure built: {struct_type} (Total: {self.structures_built})")
        
        elif event_type == 'structure_destroyed':
            self.structures_destroyed += 1
            struct_type = data.get('type', 'Unknown')
            print(f"💥 Structure destroyed: {struct_type} (Total: {self.structures_destroyed})")


class GameEventLogger(Observer):
    """Event logger useful for debugging; records recent events.

    When `verbose` is True the logger will also print events to stdout.
    """
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.event_log = []
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        self.event_log.append({'type': event_type, 'data': data})
        
        if self.verbose:
            print(f"🎮 Event: {event_type} | Data: {data}")
        
        # Limitar tamaño del log
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-50:]
    
    def get_recent_events(self, count=10):
        """Obtiene los últimos N eventos"""
        return self.event_log[-count:]
