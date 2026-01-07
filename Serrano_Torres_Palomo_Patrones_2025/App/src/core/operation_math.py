from .operation_base import OperationModule
from .sprite_loader import load_sprite_from_assets


class SumModule(OperationModule):
    def get_symbol(self):
        return "+"

    def operate(self, a, b):
        return a + b

    def _load_sprite(self):
        self.sprite = load_sprite_from_assets("sum_module_minimal.png")


class MultiplyModule(OperationModule):
    def get_symbol(self):
        return "x"

    def operate(self, a, b):
        return a * b

    def _load_sprite(self):
        self.sprite = load_sprite_from_assets("mul_module_minimal.png")


class DivModule(OperationModule):
    def get_symbol(self):
        return "÷"

    def operate(self, a, b):
        if b != 0:
            return a // b
        return 0

    def _load_sprite(self):
        self.sprite = load_sprite_from_assets("div_module_minimal.png")
