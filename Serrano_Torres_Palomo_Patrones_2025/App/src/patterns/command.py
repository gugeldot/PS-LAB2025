"""
Command Pattern - Encapsular acciones como objetos

Permite deshacer/rehacer operaciones y mantener historial de acciones.
Útil para construcción/destrucción de estructuras.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Command(ABC):
    """Interfaz base para comandos"""
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Ejecuta el comando
        Returns: True si tuvo éxito, False si falló
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Deshace el comando
        Returns: True si tuvo éxito, False si falló
        """
        pass
    
    def get_description(self) -> str:
        """Retorna descripción del comando para UI"""
        return self.__class__.__name__


class BuildStructureCommand(Command):
    """Comando para construir una estructura"""
    
    def __init__(self, gameManager, creator, position):
        self.gameManager = gameManager
        self.creator = creator
        self.position = position
        self.structure = None
        self.cost = creator.getCost()
    
    def execute(self) -> bool:
        """Construye la estructura si hay puntos suficientes"""
        if getattr(self.gameManager, 'points', 0) < self.cost:
            return False
        
        try:
            # Crear estructura
            self.structure = self.creator.createStructure(self.position, self.gameManager)
            
            # Agregar al mapa y lista
            gx, gy = int(self.position[0]), int(self.position[1])
            if not self.gameManager.map.placeStructure(gx, gy, self.structure):
                return False
            
            if not hasattr(self.gameManager, 'structures'):
                self.gameManager.structures = []
            self.gameManager.structures.append(self.structure)
            
            # Deducir puntos
            self.gameManager.points -= self.cost
            
            # Notificar observadores si existe el sistema
            if hasattr(self.gameManager, 'notify'):
                self.gameManager.notify('structure_built', {
                    'type': self.structure.__class__.__name__,
                    'position': self.position,
                    'cost': self.cost
                })
            
            return True
        except Exception as e:
            print(f"Error executing BuildStructureCommand: {e}")
            return False
    
    def undo(self) -> bool:
        """Deshace la construcción, devolviendo puntos"""
        if not self.structure:
            return False
        
        try:
            # Quitar del mapa
            gx, gy = int(self.position[0]), int(self.position[1])
            self.gameManager.map.removeStructure(gx, gy)
            
            # Quitar de lista
            if self.structure in self.gameManager.structures:
                self.gameManager.structures.remove(self.structure)
            
            # Devolver puntos
            self.gameManager.points += self.cost
            
            # Notificar observadores
            if hasattr(self.gameManager, 'notify'):
                self.gameManager.notify('structure_destroyed', {
                    'type': self.structure.__class__.__name__,
                    'position': self.position,
                    'refund': self.cost
                })
            
            return True
        except Exception as e:
            print(f"Error undoing BuildStructureCommand: {e}")
            return False
    
    def get_description(self) -> str:
        struct_type = self.structure.__class__.__name__ if self.structure else "Structure"
        return f"Build {struct_type} at {self.position}"


class BuildConveyorCommand(Command):
    """Comando para construir una cinta transportadora"""
    
    def __init__(self, gameManager, conveyorCreator, start_pos, end_pos):
        self.gameManager = gameManager
        self.creator = conveyorCreator
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.conveyor = None
        self.cost = conveyorCreator.getCost()
    
    def execute(self) -> bool:
        if getattr(self.gameManager, 'points', 0) < self.cost:
            return False
        
        try:
            # Crear cinta
            self.conveyor = self.creator.createStructure(
                self.start_pos, 
                self.gameManager, 
                self.end_pos
            )
            
            # Agregar a listas
            if not hasattr(self.gameManager, 'conveyors'):
                self.gameManager.conveyors = []
            self.gameManager.conveyors.append(self.conveyor)
            
            if not hasattr(self.gameManager, 'structures'):
                self.gameManager.structures = []
            self.gameManager.structures.append(self.conveyor)
            
            # Deducir puntos
            self.gameManager.points -= self.cost
            
            # Reconectar estructuras
            if hasattr(self.gameManager, '_reconnect_structures'):
                self.gameManager._reconnect_structures()
            
            return True
        except Exception as e:
            print(f"Error executing BuildConveyorCommand: {e}")
            return False
    
    def undo(self) -> bool:
        if not self.conveyor:
            return False
        
        try:
            # Quitar de listas
            if self.conveyor in self.gameManager.conveyors:
                self.gameManager.conveyors.remove(self.conveyor)
            if self.conveyor in self.gameManager.structures:
                self.gameManager.structures.remove(self.conveyor)
            
            # Devolver puntos
            self.gameManager.points += self.cost
            
            # Reconectar estructuras
            if hasattr(self.gameManager, '_reconnect_structures'):
                self.gameManager._reconnect_structures()
            
            return True
        except Exception as e:
            print(f"Error undoing BuildConveyorCommand: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Build Conveyor from {self.start_pos} to {self.end_pos}"


class CommandHistory:
    """Gestiona historial de comandos para undo/redo"""
    
    def __init__(self, max_history=50):
        self.history: List[Command] = []
        self.current_index = -1
        self.max_history = max_history
    
    def execute(self, command: Command) -> bool:
        """Ejecuta un comando y lo agrega al historial"""
        if command.execute():
            # Eliminar comandos después del índice actual (si hicimos undo)
            self.history = self.history[:self.current_index + 1]
            
            # Agregar nuevo comando
            self.history.append(command)
            self.current_index += 1
            
            # Limitar tamaño del historial
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
                self.current_index = len(self.history) - 1
            
            return True
        return False
    
    def undo(self) -> bool:
        """Deshace el último comando"""
        if not self.can_undo():
            return False
        
        command = self.history[self.current_index]
        if command.undo():
            self.current_index -= 1
            return True
        return False
    
    def redo(self) -> bool:
        """Rehace el siguiente comando"""
        if not self.can_redo():
            return False
        
        self.current_index += 1
        command = self.history[self.current_index]
        if command.execute():
            return True
        else:
            self.current_index -= 1
            return False
    
    def can_undo(self) -> bool:
        """Verifica si se puede deshacer"""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Verifica si se puede rehacer"""
        return self.current_index < len(self.history) - 1
    
    def clear(self) -> None:
        """Limpia el historial"""
        self.history.clear()
        self.current_index = -1
    
    def get_history_description(self, count=5) -> List[str]:
        """Obtiene descripciones de los últimos comandos"""
        start = max(0, self.current_index - count + 1)
        end = self.current_index + 1
        return [cmd.get_description() for cmd in self.history[start:end]]
