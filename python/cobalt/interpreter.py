from enum import Enum, auto
from dataclasses import dataclass
from collections.abc import Callable
import numpy as np
from pathlib import Path
import sys

from .stack import Stack
from .instructions import Opcode, OPCODE_FUNCTIONS, STP
from .interpreter_errors import InterpreterSyntaxError, InterpreterRuntimeError, ExecutionError

class TokenType(Enum):
    CMD = auto()    # Command
    NUM = auto()    # Number
    IDT = auto()    # Identifier
    STR = auto()    # String
    LBL = auto()    # Label

@dataclass
class Token:
    type: TokenType
    value: Opcode | float | str
    line: int

@dataclass
class Instruction:
    function: Callable | None
    argument: float | None
    line: int

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
                    tokens.append(Token(TokenType.STR, word, line_number))
                    word = ""
            elif character.isspace() and not inside_string and word in [e.name for e in Opcode]:
                tokens.append(Token(TokenType.CMD, Opcode[word], line_number))
                word = ""
            elif character.isspace() and not inside_string and word:
                try:
                    tokens.append(Token(TokenType.NUM, float(word), line_number))
                    word = ""
                except:
                    if word.endswith(":"):
                        tokens.append(Token(TokenType.LBL, word[:-1], line_number))
                        word = ""
                    else:
                        tokens.append(Token(TokenType.IDT, word, line_number))
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
        if token.type == TokenType.CMD:
            if i + 1 >= len(tokens):
                if token.value in [Opcode.PUS, Opcode.JIZ, Opcode.JUM, Opcode.JIT, Opcode.GET, Opcode.SET, Opcode.PRC]:
                    raise InterpreterSyntaxError(f"Missing argument for {token.value.name} command.", current_line)
            if token.value == Opcode.PUS and tokens[i+1].type != TokenType.NUM:
                raise InterpreterSyntaxError(f"Invalid argument for PUS. Expected a number but got {tokens[i+1].type.name}.", current_line)
            if token.value in [Opcode.JIZ, Opcode.JUM, Opcode.JIT] and tokens[i+1].type != TokenType.IDT:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a label but got {tokens[i+1].type.name}.", current_line)
            if token.value in [Opcode.GET, Opcode.SET] and tokens[i+1].type != TokenType.IDT:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a variable but got {tokens[i+1].type.name}.", current_line)
            if token.value == Opcode.PRC and tokens[i+1].type != TokenType.STR:
                raise InterpreterSyntaxError(f"Invalid argument for PRC. Expected a string but got {tokens[i+1].type.name}.", current_line)
            if token.value == Opcode.STP:
                is_STP = True

        if token.type == TokenType.IDT:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_line)
            elif tokens[i-1].value not in [Opcode.JIZ, Opcode.JUM, Opcode.JIT, Opcode.GET, Opcode.SET]:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_line)
        
        if token.type == TokenType.STR:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_line)
            elif tokens[i-1].value not in [Opcode.PRC]:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_line)
            
        if token.type == TokenType.NUM:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_line)
            elif tokens[i-1].value not in [Opcode.PUS]:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_line)

    if not is_STP:
        raise InterpreterSyntaxError("Missing STP command to stop the program.", current_line)

def parse(tokens: list[Token]) -> tuple[list[Instruction], list[str], np.array]:

    """Parses the list of tokens and returns a list of instructions, a list of messages and an array of variables. Also checks for syntax errors such as duplicate labels and undefined labels."""

    # First pass: Pair commands with their arguments and create a token pairs.
    token_pairs : list[list[Token]] = []

    for i, token in enumerate(tokens):
        if token.type in [TokenType.CMD, TokenType.LBL]:
            if token.value in [Opcode.PUS, Opcode.JIZ, Opcode.JUM, Opcode.JIT, Opcode.GET, Opcode.SET, Opcode.PRC]:
                token_pairs.append([token, tokens[i+1]])
            else:
                token_pairs.append([token, None])

    # Second pass: Create a dictionary of labels, variables and messages with their corresponding index in the instructions list, variables array and messages list respectively
    messages: list[str] = []
    dict_variables: dict[str, int] = {}
    dict_messages: dict[str, int] = {}
    labels: dict[str, int] = {}

    instruction_index = 0
    variables_index = 0
    messages_index = 0

    for token, argument in token_pairs:
        if token.type == TokenType.LBL:
            if token.value in labels:
                raise InterpreterSyntaxError(f"Duplicate label '{token.value}'", token.line)
            labels[token.value] = instruction_index
            continue
        if token.value in [Opcode.GET, Opcode.SET]:
            if argument.value not in dict_variables:
                dict_variables[argument.value] = variables_index
                variables_index += 1
        if token.value == Opcode.PRC:
            if argument.value not in dict_messages:
                dict_messages[argument.value] = messages_index
                messages.append(argument.value)
                messages_index += 1

        instruction_index += 1

    variables = np.zeros(variables_index)

    # Third pass: Check for undefined labels

    for token, argument in token_pairs:
        if token.value in [Opcode.JIT, Opcode.JIZ, Opcode.JUM]:
            if argument.value not in labels:
                raise InterpreterSyntaxError(f"Undefined label '{argument.value}'", token.line)

    # Fourth pass: Create a list of instructions with their corresponding function and argument (if any)
    instructions: list[Instruction] = []

    for token, argument in token_pairs:
        if token.type == TokenType.CMD:
            function = OPCODE_FUNCTIONS[token.value]
            if token.value in [Opcode.PUS]:
                instructions.append(Instruction(function, argument.value, token.line))
            elif token.value in [Opcode.JIT, Opcode.JIZ, Opcode.JUM]:
                instructions.append(Instruction(function, labels[argument.value], token.line))
            elif token.value in [Opcode.GET, Opcode.SET]:
                instructions.append(Instruction(function, dict_variables[argument.value], token.line))
            elif token.value == Opcode.PRC:
                instructions.append(Instruction(function, dict_messages[argument.value], token.line))
            else:
                instructions.append(Instruction(function, None, token.line))

    return instructions, messages, variables

def execute(instructions: list[Instruction], messages: list[str], variables: np.array) -> None:

    """Executes the list of instructions using the provided messages and variables."""

    stack = Stack()
    pc = 0

    while instructions[pc].function is not STP:
        instruction = instructions[pc]
        try:
            pc = instruction.function(stack, instruction.argument, messages, variables, pc=pc)
        except ExecutionError as e:
            raise InterpreterRuntimeError(e.message, instruction.line)
        if pc >= len(instructions):
            raise InterpreterRuntimeError("Program counter out of bounds. No STP command found to stop the program.", instructions[-1].line)

def run_file(file: Path) -> None:
    try:
        tokens = tokenize(file)
        validate(tokens)
        instructions, messages, variables = parse(tokens)
        execute(instructions, messages, variables)
    except InterpreterSyntaxError as e:
        sys.exit(f"Syntax Error at line {e.line}: {e.message}")
    except InterpreterRuntimeError as e:
        sys.exit(f"Runtime Error at line {e.line}: {e.message}")