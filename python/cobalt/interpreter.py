import numpy as np
from pathlib import Path

from .stack import MemStack, CallStack
from .interpreter_errors import InterpreterRuntimeError, ExecutionError
from .tokenizer import tokenize
from .preprocessor import expand_includes
from .parser import parse
from .runtime import RuntimeState, STOP_FUNCTION, OPCODE_TO_INSTRUCTION
from .ir import Statement, CompileContext, Instruction, Program, Opcode, OperandType, get_operand_type, get_token_runtime
from .config import DEFAULT_CALL_STACK_SIZE

def build_program(statements: list[Statement], context: CompileContext) -> Program:

    instructions: list[Instruction] = []

    for statement in statements:

        main_token = statement.main_token
        argument_token = statement.argument_token
        argument_type = get_operand_type(main_token)

        current_location = main_token.source_location

        if get_token_runtime(main_token):

            function = OPCODE_TO_INSTRUCTION[main_token.value]

            if argument_type == OperandType.NUMBER:
                instructions.append(Instruction(function, argument_token.value, current_location))

            elif argument_type == OperandType.LABEL:
                instructions.append(Instruction(function, context.label_table[argument_token.value], current_location))

            elif argument_type == OperandType.VARIABLE:
                instructions.append(Instruction(function, context.variable_table[argument_token.value], current_location))

            elif argument_type == OperandType.STRING:
                instructions.append(Instruction(function, context.string_table[argument_token.value], current_location))

            elif argument_type == OperandType.FUNCTION:
                instructions.append(Instruction(function, context.function_table[argument_token.value], current_location))

            else:
                instructions.append(Instruction(function, None, current_location))

    return Program(instructions, context.strings, len(context.variable_table), context.stack_size, context.entry_point)

def execute(program: Program) -> None:

    """Executes the list of instructions using the provided messages and variables."""

    instructions = program.instructions
    strings = program.strings
    n_variables = program.n_variables
    stack_size = program.stack_size
    entry_point = program.entry_point

    initialized_variables = [False] * n_variables
    variables = np.zeros(n_variables, dtype=np.float64)
    mem_stack = MemStack(stack_size)
    call_stack = CallStack(DEFAULT_CALL_STACK_SIZE)

    runtime_state = RuntimeState(mem_stack, call_stack, entry_point, variables, strings, initialized_variables)

    if runtime_state.pc >= len(instructions):
        raise InterpreterRuntimeError(f"Program counter out of bounds. No {Opcode.STP.name} command found to stop the program.", instructions[-1].source_location)

    while instructions[runtime_state.pc].function is not STOP_FUNCTION:
        instruction = instructions[runtime_state.pc]
        try:
            instruction.function(runtime_state, instruction.argument)
        except ExecutionError as e:
            raise InterpreterRuntimeError(e.message, instruction.source_location)
        if runtime_state.pc >= len(instructions):
            raise InterpreterRuntimeError(f"Program counter out of bounds. No {Opcode.STP.name} command found to stop the program.", instructions[-1].source_location)

def run_file(file: Path) -> None:
        
    tokens = tokenize(file)
    tokens = expand_includes(tokens, file)
    statements, context = parse(tokens, file)
    program = build_program(statements, context)
    execute(program)