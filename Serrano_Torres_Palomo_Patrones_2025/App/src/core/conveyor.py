"""Conveyor implementation.

This module provides :class:`Conveyor`, a lightweight structure that
transports numeric items between other structures using an internal queue.

The conveyor stores items as dictionaries with ``value`` and ``position``
keys where ``position`` progresses from 0.0 to 1.0 during transmission.
"""

import pygame as pg
from collections import deque
from .structure import Structure
from patterns.iterator import FlowIterator


class Conveyor(Structure):
    """Conveyor belt that transports numbers between structures.

    Attributes
    ----------
    start_pos, end_pos: pg.Vector2
        Pixel coordinates for the conveyor endpoints.
    queue: collections.deque
        Items waiting on the belt. Each item is a dict with ``value`` and
        ``position`` (0.0..1.0).
    travel_time: float
        Time in milliseconds required for an item to travel the full belt.
    """

    def __init__(self, start_pos, end_pos, gameManager, speed=1):
        self.start_pos = pg.Vector2(start_pos)
        self.end_pos = pg.Vector2(end_pos)
        self.position = self.start_pos
        self.gameManager = gameManager
        self.speed = speed
        self.queue = deque()
        self.width = 12
        self.color = (189, 195, 199)

        # precompute length and travel time
        self.length = (self.end_pos - self.start_pos).length()
        self.pixels_per_second = 100.0
        if self.length > 0:
            self.travel_time = (self.length / self.pixels_per_second) * 1000
        else:
            self.travel_time = 100

        self.outputConveyor = None

    def push(self, number):
        """Enqueue a number at the start of the conveyor."""
        self.queue.append({'value': number, 'position': 0.0})
        try:
            print(f"Conveyor: pushed {number}, queue size now {len(self.queue)}")
        except Exception:
            pass

    def pop(self):
        """Remove and return the value at the end of the belt if ready."""
        if self.queue and self.queue[0]['position'] >= 1.0:
            val = self.queue.popleft()['value']
            try:
                print(f"Conveyor: popped {val}, queue size now {len(self.queue)}")
            except Exception:
                pass
            return val
        return None

    def peek(self):
        """Return the value at the front of the queue without removing it."""
        if self.queue:
            return self.queue[0]['value']
        return None

    def isEmpty(self):
        return len(self.queue) == 0

    def isReady(self):
        """Return True if an item is positioned at the conveyor end."""
        return self.queue and self.queue[0]['position'] >= 1.0

    def size(self):
        return len(self.queue)

    def createIterator(self):
        return FlowIterator([item['value'] for item in self.queue])

    def update(self):
        """Advance item positions based on the game delta time and move items
        to the next conveyor when they reach the end."""
        delta = self.gameManager.delta_time / self.travel_time
        for item in self.queue:
            item['position'] += delta
            if item['position'] > 1.0:
                item['position'] = 1.0

        if self.queue and self.queue[0]['position'] >= 1.0 and self.outputConveyor:
            number = self.pop()
            if number is not None:
                self.outputConveyor.push(number)

    @property
    def output(self):
        return self.outputConveyor

    @output.setter
    def output(self, value):
        self.outputConveyor = value

    def connectOutput(self, conveyor):
        """Convenience to set the conveyor output."""
        self.output = conveyor

    def draw(self):
        """Render the conveyor and the queued item values on screen."""
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        start = (int(self.start_pos.x - cam.x), int(self.start_pos.y - cam.y))
        end = (int(self.end_pos.x - cam.x), int(self.end_pos.y - cam.y))
        pg.draw.line(self.gameManager.screen, self.color, start, end, self.width)

        font = pg.font.Font(None, 20)
        for item in self.queue:
            t = item['position']
            pos_x = (self.start_pos.x + (self.end_pos.x - self.start_pos.x) * t) - cam.x
            pos_y = (self.start_pos.y + (self.end_pos.y - self.start_pos.y) * t) - cam.y
            text = font.render(str(item['value']), True, (44, 62, 80))
            text_rect = text.get_rect(center=(pos_x, pos_y))
            self.gameManager.screen.blit(text, text_rect)

