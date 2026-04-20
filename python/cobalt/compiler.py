from pathlib import Path

from .tokenizer import tokenize
from .preprocessor import expand_includes
from .parser import parse
from .ir import Statement, CompileContext, TokenType, OperandType, get_operand_type
from .config import ENTRY_POINT_LABEL
from .c_templates import HELPER_FUNCTIONS, INCLUDES, LABEL, OPCODE_TO_CODE, STACK_CODE, MAIN_FUNCTION

def compile_to_c(statements: list[Statement], context: CompileContext, output_file: Path) -> None:
    
    out = open(output_file, "w")

    out.write(INCLUDES)
    out.write(STACK_CODE)
    out.write(HELPER_FUNCTIONS)

    current_scope = None

    for statement in statements:
        
        main_token = statement.main_token
        argument_token = statement.argument_token
        operand_type = get_operand_type(main_token)

        if statement.scope != current_scope and statement.scope == ENTRY_POINT_LABEL:

           out.write(MAIN_FUNCTION.substitute(
                stack_size = context.stack_size,
                n_variables = len(context.variable_table) if len(context.variable_table) > 0 else 1,
                n_strings = len(context.strings) if len(context.strings) > 0 else 1,
                strings = ", ".join([f'"{s}"' for s in context.strings]) if len(context.strings) > 0 else '"None"'
           ))

        current_scope = statement.scope
        stack_expr = "&stack" if current_scope == ENTRY_POINT_LABEL else "stack"

        if main_token.type == TokenType.LABEL:
            out.write(LABEL.substitute(value = main_token.value))

        if main_token.type == TokenType.COMMAND:
            if operand_type == OperandType.STRING:
                out.write(OPCODE_TO_CODE[main_token.value].substitute(
                    value = context.string_table[argument_token.value],
                    stack = stack_expr
                ))
            if operand_type == OperandType.VARIABLE:
                out.write(OPCODE_TO_CODE[main_token.value].substitute(
                    value = context.variable_table[argument_token.value],
                    stack = stack_expr
                ))
            if operand_type in [OperandType.FUNCTION, OperandType.LABEL, OperandType.NUMBER]:
                out.write(OPCODE_TO_CODE[main_token.value].substitute(
                    value = argument_token.value,
                    stack = stack_expr
                ))
            elif operand_type == OperandType.NONE:
                out.write(OPCODE_TO_CODE[main_token.value].substitute(
                    stack = stack_expr
                ))

    out.write("    return 0;\n")
    out.write("}\n")
    out.close()

def compile_file_to_c(file: Path) -> None:

    tokens = tokenize(file) 
    tokens = expand_includes(tokens, file)
    statements, context = parse(tokens, file)
    compile_to_c(statements, context, file.with_suffix(".c"))
    print(f"Compiled '{file.name}' to '{file.with_suffix('.c').resolve()}'.")