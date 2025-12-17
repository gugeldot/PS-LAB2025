'''
Patterns package - Contains all design pattern implementations.

Subpackages:
- decorator: Decorator pattern for upgrades (UpgradeDecorator, SpeedUpgrade, EfficiencyUpgrade)
- iterator: Iterator pattern for collections (FlowIterator)
- factory: Factory Method pattern for structure creation
- strategy: Strategy pattern for module operations
- observer: Observer pattern for events
- etc.
'''

from .decorator import UpgradeDecorator
from .iterator import FlowIterator

__all__ = ["UpgradeDecorator", "FlowIterator"]
