"""Prototype pattern utilities.

Helpers for cloning complex objects and registering reusable prototypes.
Provides `StructurePrototype`, `PrototypeRegistry` and layout helpers to
define common building configurations.
"""

from abc import ABC, abstractmethod
import copy
from typing import Dict, Any, Optional


class Prototype(ABC):
    """Interface for objects that can be cloned.

    Implementations should provide a `clone()` method returning a copy of
    the object.
    """
    
    @abstractmethod
    def clone(self):
        """Retorna una copia del objeto"""
        pass


class StructurePrototype:
    """Prototype for a structure with predefined configuration.

    Stores a creator and a configuration dictionary used when creating
    a concrete structure instance.
    """
    
    def __init__(self, creator, config: Dict[str, Any]):
        """
        Args:
            creator: El creator que se usará para construir la estructura
            config: Configuración de la estructura (posición, parámetros, etc.)
        """
        self.creator = creator
        self.config = config.copy()
    
    def clone(self) -> 'StructurePrototype':
        """Retorna una copia del prototipo"""
        return StructurePrototype(self.creator, self.config.copy())
    
    def create_structure(self, position, gameManager):
        """Crea una estructura usando la configuración del prototipo"""
        # Actualizar posición en config
        config_copy = self.config.copy()
        config_copy['position'] = position
        
        # Crear estructura usando el creator
        return self.creator.createStructure(position, gameManager)
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna la configuración del prototipo"""
        return self.config.copy()


class PrototypeRegistry:
    """Central registry for available prototypes.

    Prototypes are stored by name and returned as clones to avoid
    accidental shared mutable state.
    """
    
    def __init__(self):
        self._prototypes: Dict[str, StructurePrototype] = {}
    
    def register(self, name: str, prototype: StructurePrototype) -> None:
        """Registra un prototipo con un nombre"""
        self._prototypes[name] = prototype
        print(f"📋 Prototype registered: {name}")
    
    def unregister(self, name: str) -> bool:
        """Elimina un prototipo del registro"""
        if name in self._prototypes:
            del self._prototypes[name]
            return True
        return False
    
    def get_prototype(self, name: str) -> Optional[StructurePrototype]:
        """Obtiene un prototipo por nombre"""
        prototype = self._prototypes.get(name)
        if prototype:
            return prototype.clone()  # Retornar copia
        return None
    
    def list_prototypes(self) -> list[str]:
        """Lista todos los prototipos disponibles"""
        return list(self._prototypes.keys())
    
    def create_from_prototype(self, name: str, position, gameManager):
        """Crea una estructura desde un prototipo"""
        prototype = self.get_prototype(name)
        if prototype:
            return prototype.create_structure(position, gameManager)
        return None


# Factory para crear prototipos comunes
class PrototypeFactory:
    """Factory que crea prototipos de estructuras comunes"""
    
    @staticmethod
    def create_mine_prototype(mineCreator, number: int) -> StructurePrototype:
        """Crea prototipo de mina"""
        return StructurePrototype(mineCreator, {
            'type': 'mine',
            'number': number
        })
    
    @staticmethod
    def create_well_prototype(wellCreator, consumingNumber: int) -> StructurePrototype:
        """Crea prototipo de pozo"""
        return StructurePrototype(wellCreator, {
            'type': 'well',
            'consumingNumber': consumingNumber
        })
    
    @staticmethod
    def create_operator_prototype(operatorCreator, operation: str) -> StructurePrototype:
        """Crea prototipo de operador"""
        return StructurePrototype(operatorCreator, {
            'type': 'operator',
            'operation': operation
        })
    
    @staticmethod
    def create_conveyor_prototype(conveyorCreator) -> StructurePrototype:
        """Crea prototipo de cinta transportadora"""
        return StructurePrototype(conveyorCreator, {
            'type': 'conveyor'
        })


class LayoutPrototype:
    """Prototipo de un layout completo (conjunto de estructuras)"""
    
    def __init__(self, name: str, structures: list[Dict[str, Any]]):
        """
        Args:
            name: Nombre del layout
            structures: Lista de diccionarios con info de estructuras
                       [{'type': 'mine', 'position': (x, y), 'params': {...}}, ...]
        """
        self.name = name
        self.structures = copy.deepcopy(structures)
    
    def clone(self) -> 'LayoutPrototype':
        """Retorna una copia del layout"""
        return LayoutPrototype(self.name, self.structures)
    
    def get_structures(self) -> list[Dict[str, Any]]:
        """Retorna lista de estructuras del layout"""
        return copy.deepcopy(self.structures)


class LayoutRegistry:
    """Registro de layouts predefinidos"""
    
    def __init__(self):
        self._layouts: Dict[str, LayoutPrototype] = {}
        self._initialize_default_layouts()
    
    def _initialize_default_layouts(self):
        """Inicializa layouts predefinidos comunes"""
        # Layout básico: 2 minas -> operador suma -> pozo
        basic_layout = LayoutPrototype("basic_sum", [
            {'type': 'mine', 'position': (5, 5), 'number': 1},
            {'type': 'mine', 'position': (5, 7), 'number': 2},
            {'type': 'operator', 'position': (8, 6), 'operation': 'sum'},
            {'type': 'well', 'position': (12, 6), 'consumingNumber': 3}
        ])
        self.register("basic_sum", basic_layout)
        
        # Layout multiplicación
        mul_layout = LayoutPrototype("basic_mul", [
            {'type': 'mine', 'position': (5, 5), 'number': 2},
            {'type': 'mine', 'position': (5, 7), 'number': 3},
            {'type': 'operator', 'position': (8, 6), 'operation': 'mul'},
            {'type': 'well', 'position': (12, 6), 'consumingNumber': 6}
        ])
        self.register("basic_mul", mul_layout)
    
    def register(self, name: str, layout: LayoutPrototype) -> None:
        """Registra un layout"""
        self._layouts[name] = layout
    
    def get_layout(self, name: str) -> Optional[LayoutPrototype]:
        """Obtiene un layout por nombre"""
        layout = self._layouts.get(name)
        if layout:
            return layout.clone()
        return None
    
    def list_layouts(self) -> list[str]:
        """Lista todos los layouts disponibles"""
        return list(self._layouts.keys())
