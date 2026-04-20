from dataclasses import dataclass
from .stack import MemStack, CallStack
from .ir import Opcode
import numpy as np
from .interpreter_errors import ExecutionError

@dataclass
class RuntimeState:
    mem_stack: MemStack
    call_stack: CallStack
    pc: int
    variables: np.array
    strings: list[str]
    initialized_variables: list[bool]

def REA(r: RuntimeState, argument: float | int | None) -> None:
    try:
        number = float(input())
    except:
        raise ExecutionError(f"Invalid input. Expected a number.")
    r.mem_stack.push(number)
    r.pc += 1

def PUS(r: RuntimeState, argument: float | int | None) -> None:
    r.mem_stack.push(argument)
    r.pc += 1

def DEP(r: RuntimeState, argument: float | int | None) -> None:
    r.mem_stack.push(r.mem_stack.depth())
    r.pc += 1

def POP(r: RuntimeState, argument: float | int | None) -> None  :
    r.mem_stack.pop()
    r.pc +=  1

def SWP(r: RuntimeState, argument: float | int | None) -> None:
    r.mem_stack.swap()
    r.pc += 1

def DUP(r: RuntimeState, argument: float | int | None) -> None:
    r.mem_stack.duplicate()
    r.pc += 1
 
def EQU(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a == b else 0)
    r.pc += 1

def NEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a != b else 0)
    r.pc += 1

def GTH(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a > b else 0)
    r.pc += 1

def LTH(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a < b else 0)
    r.pc += 1

def GEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a >= b else 0)
    r.pc += 1
 
def LEQ(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(1 if a <= b else 0)
    r.pc += 1
  
def AND(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for AND. Expected 0 or 1 but got {a} and {b}.")
    r.mem_stack.push(1 if a and b else 0)
    r.pc += 1

def OR(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    if a not in [0, 1] or b not in [0, 1]:
        raise ExecutionError(f"Invalid operands for OR. Expected 0 or 1 but got {a} and {b}.")
    r.mem_stack.push(1 if a or b else 0)
    r.pc += 1

def NOT(r: RuntimeState, argument: float | int | None) -> None:
    a = r.mem_stack.pop()
    if a not in [0, 1]:
        raise ExecutionError(f"Invalid operand for NOT. Expected 0 or 1 but got {a}.")
    r.mem_stack.push(1 if not a else 0)
    r.pc += 1

def ADD(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(a + b)
    r.pc += 1

def SUB(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(a - b)
    r.pc += 1

def MUL(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    r.mem_stack.push(a * b)
    r.pc += 1

def DIV(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    if b == 0:
        raise ExecutionError(f"Division by zero.")
    r.mem_stack.push(a / b)
    r.pc += 1

def MOD(r: RuntimeState, argument: float | int | None) -> None:
    b = r.mem_stack.pop()
    a = r.mem_stack.pop()
    if b == 0:
        raise ExecutionError(f"Modulo by zero.")
    r.mem_stack.push(a % b)
    r.pc += 1

def JIZ(r: RuntimeState, argument: float | int | None) -> None:
    a = r.mem_stack.pop()
    if a == 0:
        r.pc = argument
    else:
        r.pc += 1

def JIT(r: RuntimeState, argument: float | int | None) -> None:
    a = r.mem_stack.pop()
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
    print(r.mem_stack.peek())
    r.pc += 1

def SET(r: RuntimeState, argument: float | int | None) -> None:
    r.variables[argument] = r.mem_stack.pop()
    r.initialized_variables[argument] = True
    r.pc += 1
  
def GET(r: RuntimeState, argument: float | int | None) -> None:
    if not r.initialized_variables[argument]:
        raise ExecutionError(f"Variable is not initialized.")    
    r.mem_stack.push(r.variables[argument])
    r.pc += 1

def CAL(r: RuntimeState, argument: float | int | None) -> None:
    r.call_stack.push(r.pc + 1)
    r.pc = argument

def RET(r: RuntimeState, argument: float | int | None) -> None:
    if r.call_stack.sp < 0:
        raise ExecutionError(f"Call stack underflow. No function to return from.")
    r.pc = r.call_stack.pop()

def STOP_FUNCTION(r: RuntimeState, argument: float | int | None) -> None:
    pass

OPCODE_TO_INSTRUCTION = {
    Opcode.REA: REA,
    Opcode.PUS: PUS,
    Opcode.DEP: DEP,
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
    Opcode.CAL: CAL,
    Opcode.RET: RET,
    Opcode.STP: STOP_FUNCTION
}