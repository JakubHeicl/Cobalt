from enum import Enum, auto
from dataclasses import dataclass
from collections.abc import Callable
import numpy as np
from pathlib import Path
import sys

from .stack import Stack
from .instructions import *
from .interpreter_errors import InterpreterSyntaxError, InterpreterRuntimeError, ExecutionError

DEFAULT_STACK_SIZE = 64

class TokenType(Enum):
    COMMAND = auto()    # Command
    POS_INT = auto()    # Integer
    FLOAT = auto()  # Float
    IDENTIFIER = auto()    # Identifier
    STRING = auto()    # String
    LABEL = auto()    # Label

@dataclass
class Token:
    type: TokenType
    value: Opcode | float | str
    line: int

@dataclass
class Instruction:
    function: Callable | None
    argument: float | int | None
    line: int

@dataclass
class Program:
    instructions: list[Instruction]
    strings: list[str]
    variables: np.array
    stack_size: int

def tokenize(file: Path) -> list[Token]:
    """
    Tokenizes the source code and returns a list of tokens.
    Also checks for syntax errors such as unclosed strings and invalid commands.
    Args:
        file (Path): The path to the source code file.
    Returns:
        list[Token]: A list of tokens.
    """
    tokens: list[Token] = []
    
    try:
        f = open(file, "r")
    except FileNotFoundError:
        raise InterpreterSyntaxError(f"File '{file}' not found.", 0)

    lines = f.readlines()

    for i, line in enumerate(lines):

        line_number = i + 1

        if line.strip() == "" or line.strip().startswith("#"):
            continue
        line = line.rstrip("\n")
        inside_string = False
        word = ""

        for character in line+" ":
            if character == "#" and not inside_string: break

            if character == '"':
                inside_string = not inside_string
                if not inside_string:
                    tokens.append(Token(TokenType.STRING, word, line_number))
                    word = ""
            elif character.isspace() and not inside_string and word in [e.name for e in Opcode]:
                tokens.append(Token(TokenType.COMMAND, Opcode[word], line_number))
                word = ""
            elif character.isspace() and not inside_string and word:
                try:
                    pos_int = int(word)
                    if pos_int < 0:
                        raise ValueError
                    tokens.append(Token(TokenType.POS_INT, pos_int, line_number))
                    word = ""
                except:
                    try:
                        tokens.append(Token(TokenType.FLOAT, float(word), line_number))
                        word = ""
                    except:
                        if word.endswith(":"):
                            tokens.append(Token(TokenType.LABEL, word[:-1], line_number))
                            word = ""
                        else:
                            tokens.append(Token(TokenType.IDENTIFIER, word, line_number))
                            word = ""
            elif character.isspace() and not inside_string: 
                continue
            else:
                word += character

        if inside_string:
            raise InterpreterSyntaxError(f"Unclosed string", line_number)
    f.close()
    return tokens

def validate(tokens: list[Token]) -> None:

    """Validates the list of tokens for syntax errors such as missing arguments, invalid argument types and missing STP command."""

    if len(tokens) == 0:
        raise InterpreterSyntaxError("Empty program. No tokens found.", 0)

    current_line = 0
    is_STP = False
    for i, token in enumerate(tokens):
        current_line = token.line
        if token.type == TokenType.COMMAND:
            if token.value == Opcode.STK and i != 0:
                raise InterpreterSyntaxError(f"STK command must be the first command in the program.", current_line)
            if i + 1 >= len(tokens):
                if token.value in OPCODES_WITH_ARGUMENT:
                    raise InterpreterSyntaxError(f"Missing argument for {token.value.name} command.", current_line)
            if token.value in OPCODES_WITH_FLOAT_ARGUMENT and (tokens[i+1].type != TokenType.POS_INT and tokens[i+1].type != TokenType.FLOAT):
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a number but got {tokens[i+1].type.name}.", current_line)
            if token.value in OPCODES_WITH_POS_INT_ARGUMENT and tokens[i+1].type != TokenType.POS_INT:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a positive integer but got {tokens[i+1].type.name}.", current_line)
            if token.value in OPCODES_WITH_LABEL_ARGUMENT and tokens[i+1].type != TokenType.IDENTIFIER:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a label but got {tokens[i+1].type.name}.", current_line)
            if token.value in OPCODES_WITH_VARIABLE_ARGUMENT and tokens[i+1].type != TokenType.IDENTIFIER:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a variable but got {tokens[i+1].type.name}.", current_line)
            if token.value in OPCODES_WITH_STRING_ARGUMENT and tokens[i+1].type != TokenType.STRING:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a string but got {tokens[i+1].type.name}.", current_line)
            if token.value == Opcode.STP:
                is_STP = True

        if token.type == TokenType.IDENTIFIER:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_line)
            elif tokens[i-1].value not in OPCODES_WITH_IDENTIFIER_ARGUMENT:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_line)
        
        if token.type == TokenType.STRING:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_line)
            elif tokens[i-1].value not in OPCODES_WITH_STRING_ARGUMENT:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_line)
            
        if token.type == TokenType.POS_INT or token.type == TokenType.FLOAT:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_line)
            elif tokens[i-1].value not in OPCODES_WITH_FLOAT_ARGUMENT and tokens[i-1].value not in OPCODES_WITH_POS_INT_ARGUMENT:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_line)

    if not is_STP:
        raise InterpreterSyntaxError("Missing STP command to stop the program.", current_line)

def parse(tokens: list[Token]) -> Program:

    """Parses the list of tokens and returns a list of instructions, a list of messages and an array of variables. Also checks for syntax errors such as duplicate labels and undefined labels."""

    # First pass: Pair commands with their arguments and create a token pairs.
    token_pairs : list[list[Token]] = []

    for i, token in enumerate(tokens):
        if token.type in [TokenType.COMMAND, TokenType.LABEL]:
            if token.value in OPCODES_WITH_ARGUMENT:
                token_pairs.append([token, tokens[i+1]])
            else:
                token_pairs.append([token, None])

    # Check if the first command is STK to determine the stack size. If not, use the default stack size of 64.

    first_token, first_argument = token_pairs[0]
    if first_token.value == Opcode.STK:
        stack_size = first_argument.value
        token_pairs.pop(0)
    else:
        stack_size = DEFAULT_STACK_SIZE

    # Second pass: Create a dictionary of labels, variables and strings with their corresponding index in the instructions list, variables array and messages list respectively

    strings: list[str] = []
    variable_table: dict[str, int] = {}
    string_table: dict[str, int] = {}
    label_table: dict[str, int] = {}

    instruction_index = 0

    for token, argument in token_pairs:
        if token.type == TokenType.LABEL:
            if token.value in label_table:
                raise InterpreterSyntaxError(f"Duplicate label '{token.value}'", token.line)
            label_table[token.value] = instruction_index
            continue
        if token.value in [Opcode.GET, Opcode.SET]:
            if argument.value not in variable_table:
                variable_table[argument.value] = len(variable_table)
        if token.value == Opcode.PRC:
            if argument.value not in string_table:
                string_table[argument.value] = len(string_table)
                strings.append(argument.value)

        instruction_index += 1

    variables = np.zeros(len(variable_table))

    # Third pass: Check for undefined labels

    for token, argument in token_pairs:
        if token.value in OPCODES_WITH_LABEL_ARGUMENT:
            if argument.value not in label_table:
                raise InterpreterSyntaxError(f"Undefined label '{argument.value}'", token.line)

    # Fourth pass: Create a list of instructions with their corresponding function and argument (if any)
    instructions: list[Instruction] = []

    for token, argument in token_pairs:
        if token.type == TokenType.COMMAND:

            function = OPCODE_FUNCTIONS[token.value]

            if token.value in OPCODES_WITH_FLOAT_ARGUMENT:
                instructions.append(Instruction(function, argument.value, token.line))

            elif token.value in OPCODES_WITH_LABEL_ARGUMENT:
                instructions.append(Instruction(function, label_table[argument.value], token.line))

            elif token.value in OPCODES_WITH_VARIABLE_ARGUMENT:
                instructions.append(Instruction(function, variable_table[argument.value], token.line))

            elif token.value in OPCODES_WITH_STRING_ARGUMENT:
                instructions.append(Instruction(function, string_table[argument.value], token.line))

            else:
                instructions.append(Instruction(function, None, token.line))

    return Program(instructions, strings, variables, stack_size)

def execute(program: Program) -> None:

    """Executes the list of instructions using the provided messages and variables."""

    instructions = program.instructions
    strings = program.strings
    variables = program.variables
    stack_size = program.stack_size

    initialized_variables = [False] * len(variables)

    stack = Stack(stack_size)

    runtime_state = RuntimeState(stack, variables, strings, initialized_variables)

    while instructions[runtime_state.pc].function is not STP:
        instruction = instructions[runtime_state.pc]
        try:
            instruction.function(runtime_state, instruction.argument)
        except ExecutionError as e:
            raise InterpreterRuntimeError(e.message, instruction.line)
        if runtime_state.pc >= len(instructions):
            raise InterpreterRuntimeError("Program counter out of bounds. No STP command found to stop the program.", instructions[-1].line)

def run_file(file: Path) -> None:
    try:
        tokens = tokenize(file)
        validate(tokens)
        program = parse(tokens)
        execute(program)
    except InterpreterSyntaxError as e:
        sys.exit(f"Syntax Error at line {e.line}: {e.message}")
    except InterpreterRuntimeError as e:
        sys.exit(f"Runtime Error at line {e.line}: {e.message}")