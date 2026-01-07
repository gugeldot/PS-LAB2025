"""Singleton pattern utilities.

Provides two simple singleton implementations used across the project:
`SingletonMeta` (a metaclass) and `Singleton` (a base class). Both ensure
that only one instance of a class exists.
"""


class SingletonMeta(type):
    """Metaclass implementing the singleton pattern.

    Usage:

    class MyClass(metaclass=SingletonMeta):
        pass
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton:
    """Base-class implementing a simple singleton.

    Subclass to get a class with at most one instance.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    