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


class SpeedUpgrade(UpgradeDecorator):
    """Concrete decorator that speeds up conveyors (reduces travel_time).

    If the wrapped target exposes a `travel_time` attribute (as `Conveyor`
    does), this decorator will apply a one-time reduction to it and mark
    the target as speed-upgraded to avoid repeated application.
    """
    def __init__(self, target):
        super().__init__(target)
        # apply upgrade only once
        try:
            if hasattr(self.target, 'travel_time') and not getattr(self.target, '_speed_upgraded', False):
                # reduce travel time to make it faster (cap to avoid too small)
                self.target.travel_time = max(50, int(self.target.travel_time * 0.5))
                setattr(self.target, '_speed_upgraded', True)
        except Exception:
            pass

    def update(self):
        # delegate to wrapped structure
        try:
            return self.target.update()
        except Exception:
            pass

    def draw(self):
        # draw wrapped structure then an indicator ring for the upgrade
        try:
            self.target.draw()
        except Exception:
            pass

        try:
            import pygame as pg
            if hasattr(self.target, 'position') and hasattr(self.target, 'gameManager'):
                pos = self.target.position
                radius = getattr(self.target, 'radius', 12)
                pg.draw.circle(self.target.gameManager.screen, (0, 150, 255), (int(pos.x), int(pos.y)), radius + 6, 2)
        except Exception:
            pass


class EfficiencyUpgrade(UpgradeDecorator):
    """Concrete decorator that improves production/efficiency.

    If the wrapped target is a `Mine` (has `number`) the produced value is
    increased (multiplied). If the target has another numeric production
    attribute this will try a reasonable best-effort change. A flag is set
    to avoid repeated application.
    """
    def __init__(self, target):
        super().__init__(target)
        try:
            # double mine output if applicable
            if hasattr(self.target, 'number') and not getattr(self.target, '_efficiency_upgraded', False):
                try:
                    self.target.number = int(self.target.number * 2)
                except Exception:
                    # fallback: increment
                    self.target.number = getattr(self.target, 'number') + 1
                setattr(self.target, '_efficiency_upgraded', True)
            # if well consumingNumber exists, bump it slightly (best-effort)
            elif hasattr(self.target, 'consumingNumber') and not getattr(self.target, '_efficiency_upgraded', False):
                try:
                    self.target.consumingNumber = int(self.target.consumingNumber + 1)
                except Exception:
                    pass
                setattr(self.target, '_efficiency_upgraded', True)
        except Exception:
            pass

    def update(self):
        try:
            return self.target.update()
        except Exception:
            pass

    def draw(self):
        try:
            self.target.draw()
        except Exception:
            pass

        try:
            import pygame as pg
            if hasattr(self.target, 'position') and hasattr(self.target, 'gameManager'):
                pos = self.target.position
                radius = getattr(self.target, 'radius', 12)
                pg.draw.circle(self.target.gameManager.screen, (0, 200, 0), (int(pos.x), int(pos.y)), radius + 6, 2)
        except Exception:
            pass
