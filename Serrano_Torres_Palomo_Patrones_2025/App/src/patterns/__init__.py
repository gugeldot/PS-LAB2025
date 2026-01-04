'''
Patterns package - Contains all design pattern implementations.

Design Patterns Implemented:
1. Singleton - gameManager único
2. Factory Method - creators para estructuras
3. State - estados del juego (build, destroy, normal, conveyorBuild)
4. Iterator - FlowIterator para recorrer cintas
5. Decorator - UpgradeDecorator para mejoras
6. Observer - Sistema de eventos y notificaciones
7. Command - Comandos para undo/redo
8. Memento - Guardar/cargar estado del juego
9. Prototype - Clonar configuraciones de estructuras
10. Mediator - Coordinar comunicación entre componentes
'''

# Existing patterns
from .decorator import UpgradeDecorator
from .iterator import FlowIterator
from .singleton import SingletonMeta

# New patterns
from .observer import Observer, Subject, PointsObserver, StructureObserver, GameEventLogger
from .command import Command, BuildStructureCommand, BuildConveyorCommand, CommandHistory
from .memento import GameMemento, GameCaretaker, GameOriginator
from .prototype import Prototype, StructurePrototype, PrototypeRegistry, LayoutPrototype, LayoutRegistry
from .mediator import Mediator, GameMediator, StructureMediator

__all__ = [
    # Existing
    "UpgradeDecorator",
    "FlowIterator",
    "SingletonMeta",
    # Observer
    "Observer",
    "Subject",
    "PointsObserver",
    "StructureObserver",
    "GameEventLogger",
    # Command
    "Command",
    "BuildStructureCommand",
    "BuildConveyorCommand",
    "CommandHistory",
    # Memento
    "GameMemento",
    "GameCaretaker",
    "GameOriginator",
    # Prototype
    "Prototype",
    "StructurePrototype",
    "PrototypeRegistry",
    "LayoutPrototype",
    "LayoutRegistry",
    # Mediator
    "Mediator",
    "GameMediator",
    "StructureMediator",
]
