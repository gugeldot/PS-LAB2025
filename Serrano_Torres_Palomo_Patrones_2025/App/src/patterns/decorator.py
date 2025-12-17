from abc import ABC, abstractmethod
from core.structure import Structure


class UpgradeDecorator(Structure, ABC):
    '''
    Abstract decorator for upgrades.
    Wraps a Structure and delegates to it while allowing subclasses to add upgrade behavior.
    Uses the Decorator pattern.
    '''
    
    def __init__(self, target):
        '''
        Initialize decorator with target structure to wrap.
        
        Args:
            target: The Structure instance to decorate/upgrade
        '''
        if not isinstance(target, Structure):
            raise TypeError("Target must be a Structure instance")
        
        self.target = target
    
    @abstractmethod
    def update(self):
        '''
        Update logic - subclasses must implement.
        Should typically delegate to target.update() and add upgrade behavior.
        '''
        pass
    
    @abstractmethod
    def draw(self):
        '''
        Draw logic - subclasses must implement.
        Should typically delegate to target.draw() and optionally add visual indicators.
        '''
        pass
    
    def __getattr__(self, name):
        '''
        Delegate attribute access to the wrapped target.
        This allows the decorator to act as a transparent wrapper.
        '''
        return getattr(self.target, name)
