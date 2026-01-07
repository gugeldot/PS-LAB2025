"""Decorator patterns for structure upgrades.

This module offers decorators that wrap `core.structure.Structure` instances
to add upgrade behavior (speed, efficiency, etc.) without modifying the
original object. Decorators delegate most operations to the wrapped
structure and apply one-time modifications where appropriate.
"""

from abc import ABC, abstractmethod
from core.structure import Structure


class UpgradeDecorator(Structure, ABC):
    """Abstract decorator for upgrades.

    Wraps a Structure and delegates to it while allowing subclasses to add
    upgrade-related behavior. Subclasses must implement `update` and
    `draw` and typically call the wrapped target's implementations.
    """
    
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
    
        import pygame as pg
        if hasattr(self.target, 'position') and hasattr(self.target, 'gameManager'):
            pos = self.target.position
            radius = getattr(self.target, 'radius', 12)
            cam = getattr(self.target.gameManager, 'camera', pg.Vector2(0, 0))
            draw_pos = (int(pos.x - cam.x), int(pos.y - cam.y))
            pg.draw.circle(self.target.gameManager.screen, (0, 150, 255), draw_pos, radius + 6, 2)
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
            # If this decorates a Conveyor-like object, reduce its travel_time once
            if hasattr(self.target, 'travel_time') and not getattr(self.target, '_speed_upgraded', False):
                # reduce travel time to make it faster (cap to avoid too small)
                self.target.travel_time = max(50, int(self.target.travel_time * 0.5))
                setattr(self.target, '_speed_upgraded', True)

            # If this decorates a Mine, also reduce the global production interval
            # so the mine produces faster. We try to update the gameManager if available.
            if hasattr(self.target, 'number') and not getattr(self.target, '_speed_upgraded', False):
                try:
                    gm = getattr(self.target, 'gameManager', None)
                    # mark mine as speed-upgraded to avoid repeated application
                    setattr(self.target, '_speed_upgraded', True)
                    if gm is not None:
                        # ensure base interval exists
                        if not hasattr(gm, '_base_production_interval'):
                            gm._base_production_interval = int(getattr(gm, 'production_interval', 2000))
                        # apply a one-time halving of the production interval
                        try:
                            gm.production_interval = max(100, int(gm._base_production_interval * 0.5))
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    def update(self):
        """Delegate update to the wrapped structure.

        Subclasses may extend this method; the base implementation forwards
        to the wrapped structure and suppresses exceptions to preserve
        runtime stability in the game loop.
        """
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
                    old = int(getattr(self.target, 'number', 0))
                except Exception:
                    try:
                        old = int(self.target.number)
                    except Exception:
                        old = 0
                try:
                    new = int(old * 2)
                    self.target.number = new
                except Exception:
                    # fallback: increment
                    try:
                        self.target.number = int(getattr(self.target, 'number', 0)) + 1
                        new = int(self.target.number)
                    except Exception:
                        new = getattr(self.target, 'number', 0)
                setattr(self.target, '_efficiency_upgraded', True)
                # update any in-flight items on conveyors so the change is visible immediately
                try:
                    gm = getattr(self.target, 'gameManager', None)
                    delta = int(new) - int(old)
                    if gm is not None and delta != 0:
                        for conv in getattr(gm, 'conveyors', []):
                            try:
                                for item in conv.queue:
                                    try:
                                        item['value'] = int(item.get('value', 0)) + delta
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                except Exception:
                    pass
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
                cam = getattr(self.target.gameManager, 'camera', pg.Vector2(0, 0))
                draw_pos = (int(pos.x - cam.x), int(pos.y - cam.y))
                pg.draw.circle(self.target.gameManager.screen, (0, 200, 0), draw_pos, radius + 6, 2)
        except Exception:
            pass
