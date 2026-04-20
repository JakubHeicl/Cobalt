from pathlib import Path

from .interpreter_errors import InterpreterSyntaxError
from .ir import SourceLocation, Token, TokenType, Statement, CompileContext, Opcode, OperandType, get_operand_type, get_token_runtime
from .config import DEFAULT_MEM_STACK_SIZE, ENTRY_POINT_LABEL

def validate(tokens: list[Token], file: Path) -> None:
    """
    Validates the list of tokens for syntax errors such as missing arguments, invalid argument types and missing STP command.
    """
    if len(tokens) == 0:
        raise InterpreterSyntaxError("Empty program. No tokens found.", SourceLocation(file, 0))

    is_STP = False
    is_ENTRY_POINT_LABEL = False

    for i, token in enumerate(tokens):

        operand_type = get_operand_type(token)

        current_location = token.source_location
        if token.type == TokenType.COMMAND:

            if token.value == Opcode.STK and i != 0:
                raise InterpreterSyntaxError(f"{Opcode.STK.name} command must be the first command in the program.", current_location)
            if i + 1 >= len(tokens):
                if operand_type != OperandType.NONE:
                    raise InterpreterSyntaxError(f"Missing argument for {token.value.name} command.", current_location)
            if operand_type == OperandType.NUMBER and (tokens[i+1].type != TokenType.POS_INT and tokens[i+1].type != TokenType.FLOAT):
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a number but got {tokens[i+1].type.name}.", current_location)
            if operand_type == OperandType.POS_INT and tokens[i+1].type != TokenType.POS_INT:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a positive integer but got {tokens[i+1].type.name}.", current_location)
            if operand_type == OperandType.LABEL and tokens[i+1].type != TokenType.IDENTIFIER:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a label but got {tokens[i+1].type.name}.", current_location)
            if operand_type == OperandType.VARIABLE and tokens[i+1].type != TokenType.IDENTIFIER:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a variable but got {tokens[i+1].type.name}.", current_location)
            if operand_type == OperandType.FUNCTION and tokens[i+1].type != TokenType.IDENTIFIER:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected an identifier for a function but got {tokens[i+1].type.name}.", current_location)
            if operand_type == OperandType.STRING and tokens[i+1].type != TokenType.STRING:
                raise InterpreterSyntaxError(f"Invalid argument for {token.value.name}. Expected a string but got {tokens[i+1].type.name}.", current_location)
            if token.value == Opcode.STP:
                is_STP = True
        if token.type == TokenType.LABEL and token.value == ENTRY_POINT_LABEL:
            is_ENTRY_POINT_LABEL = True

        if token.type == TokenType.IDENTIFIER:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_location)
            elif get_operand_type(tokens[i-1]) not in [OperandType.LABEL, OperandType.VARIABLE, OperandType.FUNCTION]:
                raise InterpreterSyntaxError(f"Unexpected identifier '{token.value}'", current_location)
        
        if token.type == TokenType.STRING:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_location)
            elif get_operand_type(tokens[i-1]) != OperandType.STRING:
                raise InterpreterSyntaxError(f"Unexpected string '{token.value}'", current_location)
            
        if token.type == TokenType.POS_INT or token.type == TokenType.FLOAT:
            if i == 0:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_location)
            elif get_operand_type(tokens[i-1]) not in [OperandType.NUMBER, OperandType.POS_INT]:
                raise InterpreterSyntaxError(f"Unexpected number '{token.value}'", current_location)

    if not is_STP:
        raise InterpreterSyntaxError(f"Missing {Opcode.STP.name} command to stop the program.", current_location)
    if not is_ENTRY_POINT_LABEL:
        raise InterpreterSyntaxError(f"The program must include the entry label '{ENTRY_POINT_LABEL}:'", current_location)
    
def group_statements(tokens: list[Token]) -> list[Statement]:
    """
    Groups the list of tokens into statements, which consist of a main token (command or label) and an optional argument token. Also checks for syntax errors such as missing arguments and invalid argument types.
    """
    statements : list[Statement] = []

    for i, token in enumerate(tokens):

        argument_type = get_operand_type(token)
        if token.type in [TokenType.COMMAND, TokenType.LABEL]:
            if argument_type != OperandType.NONE:
                statements.append(Statement(token, tokens[i+1])) 
            else:
                statements.append(Statement(token, None))

    return statements

def collect_symbols(statements: list[Statement]) -> CompileContext:

    strings: list[str] = []
    variable_table: dict[str, int] = {}
    string_table: dict[str, int] = {}
    label_table: dict[str, int] = {}
    scope_table: dict[str, str | None] = {}
    function_table: dict[str, int] = {}

    instruction_index = 0
    current_scope: str | None = None

    stack_size = DEFAULT_MEM_STACK_SIZE

    for statement in statements:

        main_token = statement.main_token
        argument_token = statement.argument_token
        argument_type = get_operand_type(main_token)
        current_location = main_token.source_location

        if main_token.type == TokenType.LABEL:
            if main_token.value in label_table:
                raise InterpreterSyntaxError(f"Duplicate label '{main_token.value}'.", current_location)
            label_table[main_token.value] = instruction_index
            if main_token.value == ENTRY_POINT_LABEL:
                if current_scope is not None:
                    raise InterpreterSyntaxError(f"Entry label '{ENTRY_POINT_LABEL}:' must be defined after all functions.", current_location)
                current_scope = ENTRY_POINT_LABEL
            scope_table[main_token.value] = current_scope

        statement.scope = current_scope

        if main_token.value == Opcode.FUN:
            if argument_token.value in function_table:
                raise InterpreterSyntaxError(f"Duplicate function definition '{argument_token.value}'.", current_location)
            if current_scope is not None:
                raise InterpreterSyntaxError(f"Function definition '{argument_token.value}' must be defined before the entry label '{ENTRY_POINT_LABEL}' and outside any other function.", current_location)
            function_table[argument_token.value] = instruction_index
            current_scope = argument_token.value

        if main_token.value == Opcode.RET:
            if current_scope is None or current_scope == ENTRY_POINT_LABEL:
                raise InterpreterSyntaxError(f"{Opcode.RET.name} command must be inside a function.", current_location)
            current_scope = None

        if argument_type == OperandType.VARIABLE:
            if argument_token.value not in variable_table:
                variable_table[argument_token.value] = len(variable_table)

        if argument_type == OperandType.STRING:
            if argument_token.value not in string_table:
                string_table[argument_token.value] = len(string_table)
                strings.append(argument_token.value)

        if main_token.value == Opcode.STK:
            stack_size = argument_token.value    

        if main_token.value == Opcode.STP and current_scope != ENTRY_POINT_LABEL:
            raise InterpreterSyntaxError(f"{Opcode.STP.name} command must be in the main program, not inside a function.", current_location)        

        if get_token_runtime(main_token):
            instruction_index += 1

    entry_point = label_table[ENTRY_POINT_LABEL] 

    return CompileContext(variable_table, string_table, label_table, function_table, scope_table, strings, stack_size, entry_point)

def validate_references(statements: list[Statement], context: CompileContext) -> None:

    for statement in statements:

        main_token = statement.main_token
        argument_token = statement.argument_token
        argument_type = get_operand_type(main_token)
        current_location = main_token.source_location

        if get_token_runtime(main_token) and statement.scope is None:
                if main_token.type == TokenType.COMMAND:
                    name = main_token.value.name
                elif main_token.type == TokenType.LABEL:
                    name = main_token.value
                raise InterpreterSyntaxError(f"'{name}' must be inside a function or the main program.", current_location)
        if argument_type == OperandType.LABEL:
            if argument_token.value not in context.label_table:
                raise InterpreterSyntaxError(f"Undefined label '{argument_token.value}'.", current_location)
            if statement.scope != context.scope_table[argument_token.value]:
                raise InterpreterSyntaxError(f"Jumps between scopes are not allowed. {main_token.value.name} is from scope '{statement.scope}' but jumps to label '{argument_token.value}' in scope '{context.scope_table[argument_token.value]}'.", current_location)
        if argument_type == OperandType.FUNCTION:
            if argument_token.value not in context.function_table:
                raise InterpreterSyntaxError(f"Undefined function '{argument_token.value}'.", current_location)

def parse(tokens: list[Token], file: Path) -> tuple[list[Statement], CompileContext]:

    validate(tokens, file)
    statements = group_statements(tokens)
    context = collect_symbols(statements)
    validate_references(statements, context)

    return statements, context