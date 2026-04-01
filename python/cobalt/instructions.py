from enum import Enum, auto
import numpy as np

from .stack import Stack
from .interpreter_errors import ExecutionError

class Opcode(Enum):
    REA = auto(); STP = auto(); PRC = auto() 
    PRM = auto(); ADD = auto(); SUB = auto() 
    DIV = auto(); MUL = auto(); MOD = auto()
    JIZ = auto(); JUM = auto(); JIT = auto()
    PUS = auto(); POP = auto(); DUP = auto()
    SWP = auto(); EQU = auto(); NEQ = auto()
    GTH = auto(); LTH = auto(); GEQ = auto()
    LEQ = auto(); AND = auto(); NOT = auto()
    OR  = auto(); GET = auto(); SET = auto()

def REA(Stack: Stack, *args, pc = 0) -> None:
    try:
        number = float(input())
    except:
        raise ExecutionError(f"Invalid input. Expected a number.")
    Stack.push(number)
    return pc + 1

def PUS(Stack: Stack, argument: float, *args, pc = 0) -> int:
    Stack.push(argument)
    return pc + 1

def POP(Stack: Stack, *args, pc = 0) -> int:
    Stack.pop()
    return pc + 1

def SWP(Stack: Stack, *args, pc = 0) -> int:
    Stack.swap()
    return pc + 1

def DUP(stack: Stack, *args, pc = 0) -> int:
    stack.duplicate()
    return pc + 1
 
def EQU(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a == b else 0)
    return pc + 1

def NEQ(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a != b else 0)
    return pc + 1

def GTH(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a > b else 0)
    return pc + 1

def LTH(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a < b else 0)
    return pc + 1

def GEQ(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a >= b else 0)
    return pc + 1
 
def LEQ(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(1 if a <= b else 0)
    return pc + 1
  
def AND(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for AND. Expected 0 or 1 but got {a} and {b}.")
    Stack.push(1 if a and b else 0)
    return pc + 1

def OR(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for OR. Expected 0 or 1 but got {a} and {b}.")
    Stack.push(1 if a or b else 0)
    return pc + 1

def NOT(Stack: Stack, *args, pc = 0) -> int:
    a = Stack.pop()
    if a not in [0, 1]:
        raise ExecutionError(f"Invalid operand for NOT. Expected 0 or 1 but got {a}.")
    Stack.push(1 if not a else 0)
    return pc + 1

def ADD(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(a + b)
    return pc + 1

def SUB(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(a - b)
    return pc + 1

def MUL(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    Stack.push(a * b)
    return pc + 1

def DIV(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    if b == 0:
        raise ExecutionError(f"Division by zero.")
    Stack.push(a / b)
    return pc + 1

def MOD(Stack: Stack, *args, pc = 0) -> int:
    b = Stack.pop()
    a = Stack.pop()
    if b == 0:
        raise ExecutionError(f"Modulo by zero.")
    Stack.push(a % b)
    return pc + 1

def JIZ(Stack: Stack, argument: int, *args, pc = 0) -> int:
    a = Stack.pop()
    if a == 0:
        return argument
    return pc + 1

def JIT(Stack: Stack, argument: int, *args, pc = 0) -> int:
    a = Stack.pop()
    if a not in [0, 1]:
        raise ExecutionError(f"Invalid operand for JIT. Expected 0 or 1 but got {a}.")
    if a != 0:
        return argument
    return pc + 1

def JUM(Stack: Stack, argument: int, *args, pc = 0) -> int:
    return argument
 
def PRC(Stack: Stack, argument: int, messages: list[str], *args, pc = 0) -> int:
    print(messages[argument])
    return pc + 1

def PRM(Stack: Stack, *args, pc = 0) -> int:
    print(Stack.peek())
    return pc + 1
   
def SET(Stack: Stack, argument: int, messages: list[str], variables: np.array, *args, pc = 0) -> int:
    variables[argument] = Stack.pop()
    return pc + 1
  
def GET(Stack: Stack, argument: int, messages: list[str], variables: np.array, *args, pc = 0) -> int:
    Stack.push(variables[argument])
    return pc + 1

def STP(*args, pc = 0) -> int:
    return pc

OPCODE_FUNCTIONS = {
    Opcode.REA: REA,
    Opcode.PUS: PUS,
    Opcode.POP: POP,
    Opcode.SWP: SWP,
    Opcode.DUP: DUP,
    Opcode.EQU: EQU,
    Opcode.NEQ: NEQ,
    Opcode.GTH: GTH,
    Opcode.LTH: LTH,
    Opcode.GEQ: GEQ,
    Opcode.LEQ: LEQ,
    Opcode.AND: AND,
    Opcode.NOT: NOT,
    Opcode.OR:  OR,
    Opcode.ADD: ADD,
    Opcode.SUB: SUB,
    Opcode.MUL: MUL,
    Opcode.DIV: DIV,
    Opcode.MOD: MOD,
    Opcode.JIZ: JIZ,
    Opcode.JUM: JUM,
    Opcode.JIT: JIT,
    Opcode.PRC: PRC,
    Opcode.PRM: PRM,
    Opcode.GET: GET,
    Opcode.SET: SET,
    Opcode.STP: STP
}