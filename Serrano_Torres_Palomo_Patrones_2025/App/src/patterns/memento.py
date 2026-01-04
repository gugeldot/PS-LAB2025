"""
Memento Pattern - Capturar y restaurar el estado del juego

Permite guardar snapshots del estado del juego para:
- Guardar/cargar partidas
- Checkpoint automático
- Recuperación ante errores
"""

from typing import Dict, Any, Optional
from datetime import datetime
import copy


class GameMemento:
    """Memento que almacena el estado del juego en un momento específico"""
    
    def __init__(self, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Args:
            state: Diccionario con el estado del juego
            metadata: Información adicional (timestamp, nombre, etc.)
        """
        self._state = copy.deepcopy(state)
        self._metadata = metadata or {}
        self._timestamp = datetime.now()
        
        # Agregar timestamp a metadata si no existe
        if 'timestamp' not in self._metadata:
            self._metadata['timestamp'] = self._timestamp.isoformat()
    
    def get_state(self) -> Dict[str, Any]:
        """Retorna una copia del estado guardado"""
        return copy.deepcopy(self._state)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadata del memento"""
        return self._metadata.copy()
    
    def get_timestamp(self) -> datetime:
        """Retorna el timestamp de creación"""
        return self._timestamp
    
    def get_description(self) -> str:
        """Retorna descripción legible del memento"""
        name = self._metadata.get('name', 'Unnamed')
        points = self._state.get('points', 0)
        structures = len(self._state.get('structures', []))
        return f"{name} - {points} pts, {structures} structures - {self._timestamp.strftime('%H:%M:%S')}"


class GameCaretaker:
    """Caretaker que gestiona múltiples mementos del juego"""
    
    def __init__(self, max_snapshots=10):
        self._snapshots: Dict[str, GameMemento] = {}
        self._auto_snapshots: list[GameMemento] = []
        self.max_auto_snapshots = max_snapshots
    
    def save_snapshot(self, name: str, memento: GameMemento) -> None:
        """Guarda un snapshot con nombre específico"""
        self._snapshots[name] = memento
        print(f"💾 Snapshot saved: {name}")
    
    def load_snapshot(self, name: str) -> Optional[GameMemento]:
        """Carga un snapshot por nombre"""
        return self._snapshots.get(name)
    
    def delete_snapshot(self, name: str) -> bool:
        """Elimina un snapshot"""
        if name in self._snapshots:
            del self._snapshots[name]
            return True
        return False
    
    def save_auto_snapshot(self, memento: GameMemento) -> None:
        """Guarda un snapshot automático (checkpoint)"""
        self._auto_snapshots.append(memento)
        
        # Limitar número de auto-snapshots
        if len(self._auto_snapshots) > self.max_auto_snapshots:
            self._auto_snapshots = self._auto_snapshots[-self.max_auto_snapshots:]
    
    def get_latest_auto_snapshot(self) -> Optional[GameMemento]:
        """Retorna el último snapshot automático"""
        return self._auto_snapshots[-1] if self._auto_snapshots else None
    
    def get_all_snapshots(self) -> Dict[str, GameMemento]:
        """Retorna todos los snapshots nombrados"""
        return self._snapshots.copy()
    
    def list_snapshots(self) -> list[str]:
        """Lista todos los nombres de snapshots disponibles"""
        return list(self._snapshots.keys())


class GameOriginator:
    """Originator que crea y restaura mementos del estado del juego"""
    
    def __init__(self, gameManager):
        self.gameManager = gameManager
    
    def create_memento(self, name: str = "snapshot") -> GameMemento:
        """Crea un memento del estado actual del juego"""
        try:
            state = self._capture_state()
            metadata = {
                'name': name,
                'points': getattr(self.gameManager, 'points', 0),
                'structures_count': len(getattr(self.gameManager, 'structures', [])),
                'conveyors_count': len(getattr(self.gameManager, 'conveyors', []))
            }
            return GameMemento(state, metadata)
        except Exception as e:
            print(f"Error creating memento: {e}")
            return GameMemento({}, {'name': name, 'error': str(e)})
    
    def restore_memento(self, memento: GameMemento) -> bool:
        """Restaura el estado del juego desde un memento"""
        try:
            state = memento.get_state()
            self._restore_state(state)
            print(f"✅ Game state restored: {memento.get_description()}")
            return True
        except Exception as e:
            print(f"Error restoring memento: {e}")
            return False
    
    def _capture_state(self) -> Dict[str, Any]:
        """Captura el estado actual del juego"""
        state = {
            'points': getattr(self.gameManager, 'points', 0),
            'camera': {
                'x': self.gameManager.camera.x if hasattr(self.gameManager, 'camera') else 0,
                'y': self.gameManager.camera.y if hasattr(self.gameManager, 'camera') else 0
            },
            'upgrades': {
                'speed_uses': getattr(self.gameManager, 'speed_uses_used', 0),
                'eff_uses': getattr(self.gameManager, 'eff_uses_used', 0),
                'mine_uses': getattr(self.gameManager, 'mine_uses_used', 0)
            },
            # Agregar más datos según sea necesario
        }
        return state
    
    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restaura el estado del juego desde un diccionario"""
        # Restaurar puntos
        if 'points' in state:
            self.gameManager.points = state['points']
        
        # Restaurar cámara
        if 'camera' in state and hasattr(self.gameManager, 'camera'):
            self.gameManager.camera.x = state['camera'].get('x', 0)
            self.gameManager.camera.y = state['camera'].get('y', 0)
        
        # Restaurar upgrades
        if 'upgrades' in state:
            upgrades = state['upgrades']
            self.gameManager.speed_uses_used = upgrades.get('speed_uses', 0)
            self.gameManager.eff_uses_used = upgrades.get('eff_uses', 0)
            self.gameManager.mine_uses_used = upgrades.get('mine_uses', 0)
