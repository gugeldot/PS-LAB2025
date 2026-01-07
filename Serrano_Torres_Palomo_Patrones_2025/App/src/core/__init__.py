"""Core package: collection of structures, conveyors and creators.

This package contains building blocks used by the game: conveyors,
modules (sum, mul, div, etc.), structure base classes and creators.

Only a lightweight package initializer is provided so Sphinx can import
``core`` while building autodoc pages. Implementation lives in individual
module files.
"""

__all__ = [
    'conveyor', 'conveyorCreator', 'divModule', 'divModuleCreator',
    'mergerModule', 'mergerCreator', 'mine', 'mineCreator', 'module',
    'mulModule', 'mulModuleCreator', 'operationCreator', 'operationModule',
    'operation_base', 'operation_math', 'splitterCreator', 'splitterModule',
    'sprite_loader', 'structure', 'structureCreator', 'sumModule',
    'sumModuleCreator', 'well', 'wellCreator'
]
