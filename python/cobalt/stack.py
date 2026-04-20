import numpy as np
from typing import Any

from .interpreter_errors import StackError

class Stack:
    def __init__(self, size, dtype: Any, name: str) -> None:
        self.size = size
        self.sp = -1
        self.name = name
        self.stack_array = np.zeros(size, dtype=dtype)
        
    def push(self, number: float) -> None:
        if self.sp + 1 >= self.size:
            raise StackError(f"{self.name} overflow")
        self.sp += 1
        self.stack_array[self.sp] = number

    def pop(self) -> float:
        if self.sp < 0:
            raise StackError(f"{self.name} underflow")
        value = self.stack_array[self.sp]
        self.sp -= 1
        return value
    
    def duplicate(self):
        if self.sp < 0:
            raise StackError(f"{self.name} is empty, cannot duplicate")
        self.push(self.stack_array[self.sp])

    def swap(self):
        if self.sp < 1:
            raise StackError(f"{self.name} contains only one or no value, cannot swap")
        up = self.stack_array[self.sp]
        down = self.stack_array[self.sp-1]
        self.stack_array[self.sp] = down
        self.stack_array[self.sp-1] = up

    def negate(self):
        if self.sp < 0:
            raise StackError(f"{self.name} is empty, cannot negate")
        number = self.pop()
        number *= -1
        self.push(number)
    
    def peek(self) -> float:
        if self.sp < 0:
            raise StackError(f"{self.name} is empty, cannot peek")
        return self.stack_array[self.sp]
    
    def depth(self) -> int:
        return self.sp + 1
    
class MemStack(Stack):
    def __init__(self, size):
        super().__init__(size, np.float64, "Memory stack")

class CallStack(Stack):
    def __init__(self, size):
        super().__init__(size, np.int64, "Call stack")