class FlowIterator:
    '''Iterator pattern for conveyor queue traversal'''
    
    def __init__(self, number_list):
        self.refList = number_list
        self.index = 0
    
    def __iter__(self):
        """Hace la clase iterable con for loops"""
        return self
    
    def __next__(self):
        """Implementación de protocolo iterator de Python"""
        if not self.hasNext():
            raise StopIteration
        return self.next()
    
    def hasNext(self):
        return self.index < len(self.refList)
    
    def next(self):
        if not self.hasNext():
            raise StopIteration("No more elements in conveyor")
        value = self.refList[self.index]
        self.index += 1
        return value
    
    def current(self):
        if self.hasNext():
            return self.refList[self.index]
        return None
