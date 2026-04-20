from pathlib import Path

from .interpreter_errors import InterpreterSyntaxError, InterpreterFileNotFoundError
from .ir import Token, TokenType, SourceLocation, Opcode

def tokenize(file: Path) -> tuple[list[Token], Path]:
    """
    Tokenizes the source code and returns a list of tokens.
    Also checks for syntax errors such as unclosed strings and invalid commands.
    Args:
        file (Path): The path to the source code file.
    Returns:
        list[Token]: A list of tokens.
    """
    tokens: list[Token] = []
    opcodes_names = [opcode.name for opcode in Opcode]
    file = file.resolve()
    try:
        f = open(file, "r")
    except FileNotFoundError:
        raise InterpreterFileNotFoundError(f"File '{file}' not found.", SourceLocation(file, 0))

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
                    tokens.append(Token(TokenType.STRING, word, SourceLocation(file, line_number)))
                    word = ""
            elif character.isspace() and not inside_string and word in opcodes_names:
                tokens.append(Token(TokenType.COMMAND, Opcode[word], SourceLocation(file, line_number)))
                word = ""
            elif character.isspace() and not inside_string and word:
                try:
                    pos_int = int(word)
                    if pos_int < 0:
                        raise ValueError
                    tokens.append(Token(TokenType.POS_INT, pos_int, SourceLocation(file, line_number)))
                    word = ""
                except:
                    try:
                        tokens.append(Token(TokenType.FLOAT, float(word), SourceLocation(file, line_number)))
                        word = ""
                    except:
                        if word.endswith(":"):
                            tokens.append(Token(TokenType.LABEL, word[:-1], SourceLocation(file, line_number)))
                            word = ""
                        else:
                            tokens.append(Token(TokenType.IDENTIFIER, word, SourceLocation(file, line_number)))
                            word = ""
            elif character.isspace() and not inside_string: 
                continue
            else:
                word += character

        if inside_string:
            raise InterpreterSyntaxError(f"Unclosed string", SourceLocation(file, line_number))
    f.close()
    return tokens