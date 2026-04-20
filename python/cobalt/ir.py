from enum import Enum, auto
from dataclasses import dataclass
from collections.abc import Callable
from pathlib import Path

# IR (Intermediate Representation) classes and enums.

@dataclass
class SourceLocation:
    file: Path
    line: int

class TokenType(Enum):
    COMMAND = auto()        # Command
    POS_INT = auto()        # Integer
    FLOAT = auto()          # Float
    IDENTIFIER = auto()     # Identifier
    STRING = auto()         # String
    LABEL = auto()          # Label

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
    FUN = auto(); RET = auto(); CAL = auto() 
    ICL = auto()
    DEP = auto()

@dataclass
class Token:
    type: TokenType
    value: Opcode | float | str
    source_location: SourceLocation

@dataclass
class Statement:
    main_token: Token
    argument_token: Token | None
    scope: str | None = None

@dataclass
class CompileContext:
    variable_table: dict[str, int]
    string_table: dict[str, int]
    label_table: dict[str, int]
    function_table: dict[str, int]
    scope_table: dict[str, str | None]
    strings: list[str]
    stack_size: int
    entry_point: int

@dataclass
class Instruction:
    function: Callable | None
    argument: float | int | None
    source_location: SourceLocation

@dataclass
class Program:
    instructions: list[Instruction]
    strings: list[str]
    n_variables: int
    stack_size: int
    entry_point: int

class OperandType(Enum):
    NONE = auto()
    NUMBER = auto()
    POS_INT = auto()
    STRING = auto()
    LABEL = auto()
    VARIABLE = auto()
    FUNCTION = auto()

@dataclass(frozen = True)
class OpcodeSpec:
    operand_type: OperandType = OperandType.NONE
    declaration: bool = False
    runtime: bool = True

OPCODE_SPECS = {
    Opcode.REA: OpcodeSpec(),
    Opcode.STP: OpcodeSpec(),
    Opcode.PRC: OpcodeSpec(OperandType.STRING),
    Opcode.PRM: OpcodeSpec(),
    Opcode.ADD: OpcodeSpec(),
    Opcode.SUB: OpcodeSpec(),
    Opcode.DIV: OpcodeSpec(),
    Opcode.MUL: OpcodeSpec(),
    Opcode.MOD: OpcodeSpec(),
    Opcode.JIZ: OpcodeSpec(OperandType.LABEL),
    Opcode.JUM: OpcodeSpec(OperandType.LABEL),
    Opcode.JIT: OpcodeSpec(OperandType.LABEL),
    Opcode.PUS: OpcodeSpec(OperandType.NUMBER),
    Opcode.POP: OpcodeSpec(),
    Opcode.DUP: OpcodeSpec(),
    Opcode.SWP: OpcodeSpec(),
    Opcode.EQU: OpcodeSpec(),
    Opcode.NEQ: OpcodeSpec(),
    Opcode.GTH: OpcodeSpec(),
    Opcode.LTH: OpcodeSpec(),
    Opcode.GEQ: OpcodeSpec(),
    Opcode.LEQ: OpcodeSpec(),
    Opcode.AND: OpcodeSpec(),
    Opcode.NOT: OpcodeSpec(),
    Opcode.OR:  OpcodeSpec(),
    Opcode.GET: OpcodeSpec(OperandType.VARIABLE),
    Opcode.SET: OpcodeSpec(OperandType.VARIABLE),
    Opcode.STK: OpcodeSpec(OperandType.POS_INT, declaration=True, runtime=False),
    Opcode.FUN: OpcodeSpec(OperandType.FUNCTION, declaration=True, runtime=False),
    Opcode.RET: OpcodeSpec(),
    Opcode.CAL: OpcodeSpec(OperandType.FUNCTION),
    Opcode.ICL: OpcodeSpec(OperandType.STRING, declaration=True, runtime=False),
    Opcode.DEP: OpcodeSpec(),
}

def get_operand_type(token: Token) -> OperandType:
    if token.type == TokenType.COMMAND:
        return OPCODE_SPECS[token.value].operand_type
    else:
        return OperandType.NONE
    
def get_token_runtime(token: Token) -> bool:
    if token.type == TokenType.COMMAND:
        return OPCODE_SPECS[token.value].runtime
    else:
        return False