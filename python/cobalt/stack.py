import numpy as np

from .interpreter_errors import ExecutionError

class Stack:
    def __init__(self, size = 64):
        self.size = size
        self.sp = -1
        self.mem = np.zeros(size, dtype=np.float64)

    def push(self, number: float) -> None:
        if self.sp + 1 >= self.size:
            raise ExecutionError("Stack overflow")
        self.sp += 1
        self.mem[self.sp] = number

    def pop(self) -> float:
        if self.sp < 0:
            raise ExecutionError("Stack underflow")
        value = self.mem[self.sp]
        self.sp -= 1
        return value
    
    def duplicate(self):
        if self.sp < 0:
            raise ExecutionError("Cannot duplicate an empty stack")
        self.push(self.mem[self.sp])

    def swap(self):
        if self.sp < 1:
            raise ExecutionError("Cannot swap a stack containg only one or no value")
        up = self.mem[self.sp]
        down = self.mem[self.sp-1]
        self.mem[self.sp] = down
        self.mem[self.sp-1] = up

    def negate(self):
        if self.sp < 0:
            raise ExecutionError("Cannot negate an empty stack")
        number = self.pop()
        number *= -1
        self.push(number)
    
    def peek(self) -> float:
        if self.sp < 0:
            raise ExecutionError("Cannot read from an empty stack")
        return self.mem[self.sp]