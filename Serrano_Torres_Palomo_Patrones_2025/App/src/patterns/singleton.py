"""
Singleton Pattern - Garantizar una única instancia

Proporciona dos formas de implementar Singleton:
1. SingletonMeta - Metaclase para usar con metaclass=SingletonMeta
2. Singleton - Clase base para heredar
"""


class SingletonMeta(type):
    """
    Metaclase Singleton - Garantiza una única instancia de la clase
    
    Uso:
        class MiClase(metaclass=SingletonMeta):
            pass
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# Clase base singleton
class Singleton:
    """
    Clase base Singleton - Garantiza una única instancia
    
    Uso:
        class MiClase(Singleton):
            pass
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    