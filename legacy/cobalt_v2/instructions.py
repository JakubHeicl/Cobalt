from enum import Enum, auto
import numpy as np

from .stack import Stack
from .interpreter_errors import ExecutionError

class RuntimeState:
    def __init__(self, stack: Stack, variables: np.array, strings: list[str], initialized_variables: list[bool]):
        self.stack = stack
        self.variables = variables
        self.strings = strings
        self.initialized_variables = initialized_variables
        self.pc = 0

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
    STK = auto()

OPCODES_WITH_ARGUMENT = [Opcode.STK, Opcode.PUS, Opcode.JIZ, Opcode.JUM, Opcode.JIT, Opcode.PRC, Opcode.GET, Opcode.SET]
OPCODES_WITH_STRING_ARGUMENT = [Opcode.PRC]
OPCODES_WITH_VARIABLE_ARGUMENT = [Opcode.GET, Opcode.SET]
OPCODES_WITH_LABEL_ARGUMENT = [Opcode.JIZ, Opcode.JUM, Opcode.JIT]
OPCODES_WITH_IDENTIFIER_ARGUMENT = [Opcode.JIZ, Opcode.JUM, Opcode.JIT, Opcode.GET, Opcode.SET]
OPCODES_WITH_FLOAT_ARGUMENT = [Opcode.PUS]
OPCODES_WITH_POS_INT_ARGUMENT = [Opcode.STK]

def REA(r: RuntimeState, argument: float | int | None) -> None:
    try:
        number = float(input())
    except:
        raise ExecutionError(f"Invalid input. Expected a number.")
    r.stack.push(number)
    r.pc += 1

def PUS(r: RuntimeState, argument: float | int | None) -> None:
    r.stack.push(argument)
    r.pc += 1

def POP(r: RuntimeState, argument: float | int | None) -> None  :
    r.stack.pop()
    r.pc +=  1

def SWP(r: RuntimeState, argument: float | int | None) -> None:
    r.stack.swap()
    r.pc += 1

def DUP(r: RuntimeState, argument: float | int | None) -> None:
    r.stack.duplicate()
    r.pc += 1
 
def EQU(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a == b else 0)
    r.pc += 1

def NEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a != b else 0)
    r.pc += 1

def GTH(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a > b else 0)
    r.pc += 1

def LTH(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a < b else 0)
    r.pc += 1

def GEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a >= b else 0)
    r.pc += 1
 
def LEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(1 if a <= b else 0)
    r.pc += 1
  
def AND(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for AND. Expected 0 or 1 but got {a} and {b}.")
    r.stack.push(1 if a and b else 0)
    r.pc += 1

def OR(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for OR. Expected 0 or 1 but got {a} and {b}.")
    r.stack.push(1 if a or b else 0)
    r.pc += 1

def NOT(r: RuntimeState, argument: float | int | None) -> None:
    a = r.stack.pop()
    if a not in [0, 1]:
        raise ExecutionError(f"Invalid operand for NOT. Expected 0 or 1 but got {a}.")
    r.stack.push(1 if not a else 0)
    r.pc += 1

def ADD(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(a + b)
    r.pc += 1

def SUB(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(a - b)
    r.pc += 1

def MUL(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    r.stack.push(a * b)
    r.pc += 1

def DIV(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    if b == 0:
        raise ExecutionError(f"Division by zero.")
    r.stack.push(a / b)
    r.pc += 1

def MOD(r: RuntimeState, argument: float | int | None) -> None:
    b = r.stack.pop()
    a = r.stack.pop()
    if b == 0:
        raise ExecutionError(f"Modulo by zero.")
    r.stack.push(a % b)
    r.pc += 1

def JIZ(r: RuntimeState, argument: float | int | None) -> None:
    a = r.stack.pop()
    if a == 0:
        r.pc = argument
    else:
        r.pc += 1

def JIT(r: RuntimeState, argument: float | int | None) -> None:
    a = r.stack.pop()
    if a not in [0, 1]:
        raise ExecutionError(f"Invalid operand for JIT. Expected 0 or 1 but got {a}.")
    if a != 0:
        r.pc = argument
    else:
        r.pc += 1

def JUM(r: RuntimeState, argument: float | int | None) -> None:
    r.pc = argument

def PRC(r: RuntimeState, argument: float | int | None) -> None:
    print(r.strings[argument])
    r.pc += 1

def PRM(r: RuntimeState, argument: float | int | None) -> None:
    print(r.stack.peek())
    r.pc += 1

def SET(r: RuntimeState, argument: float | int | None) -> None:
    r.variables[argument] = r.stack.pop()
    r.initialized_variables[argument] = True
    r.pc += 1
  
def GET(r: RuntimeState, argument: float | int | None) -> None:
    if not r.initialized_variables[argument]:
        raise ExecutionError(f"Variable is not initialized.")    
    r.stack.push(r.variables[argument])
    r.pc += 1

def STP(r: RuntimeState, argument: float | int | None) -> None:
    pass

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