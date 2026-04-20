from pathlib import Path
from .tokenizer import tokenize, Token, TokenType
from .interpreter_errors import InterpreterSyntaxError, InterpreterFileNotFoundError, InterpreterIncludeError
from .ir import SourceLocation, Opcode

def expand_includes(tokens: list[Token], file: Path, include_stack: list[Path] | None = None, included_files: set[Path] | None = None, source_location: SourceLocation | None = None) -> list[Token]:
    """
    Checks for include commands and includes the files. Also checks for syntax errors such as missing arguments and invalid argument types.
    """

    file = file.resolve()

    if include_stack is None:
        include_stack = []

    if included_files is None:
        included_files = set()

    if source_location is None:
        source_location = SourceLocation(file, 0)

    if file in include_stack:
        raise InterpreterIncludeError(f"Include cycle detected with file '{file.name}'.", source_location)

    include_stack.append(file)

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.value == Opcode.ICL:
            if i + 1 >= len(tokens):
                raise InterpreterSyntaxError(f"Missing argument for {Opcode.ICL.name} command.", token.source_location)
            
            argument_token = tokens[i+1]
            if argument_token.type != TokenType.STRING:
                raise InterpreterSyntaxError(f"Invalid argument for {Opcode.ICL.name}. Expected a string but got {argument_token.type.name}.", token.source_location)
            
            included_file = Path(file.parent, argument_token.value).resolve()
            
            if included_file in include_stack:
                raise InterpreterIncludeError(f"Include cycle detected with file '{included_file.name}'.", token.source_location)

            if included_file in included_files:
                tokens[i:i+2] = []
                continue

            try:
                include_tokens = tokenize(included_file)
            except InterpreterFileNotFoundError as e:
                raise InterpreterIncludeError(f"Included file '{argument_token.value}' not found.", token.source_location)
            
            include_tokens = expand_includes(include_tokens, included_file, include_stack = include_stack, included_files = included_files, source_location = token.source_location)
            
            included_files.add(included_file)
            tokens[i:i+2] = include_tokens
            continue

        i += 1

    include_stack.pop()
    return tokens