import argparse
from pathlib import Path
import sys

from .interpreter import run_file
from .compiler import compile_file_to_c
from .interpreter_errors import InterpreterSyntaxError, InterpreterRuntimeError, InterpreterIncludeError, InterpreterFileNotFoundError

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="Path to the Cobalt file to execute.")
parser.add_argument("--interpret", action="store_true", help="Interpret the Cobalt file")
parser.add_argument("--compile", action="store_true", help="Compile the Cobalt file to C")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.file is None:
        sys.exit("Usage: python -m cobalt <file.co> [--interpret] [--compile]")
    
    if not args.interpret and not args.compile:
        sys.exit("Please specify --interpret or --compile.")
    
    file = Path(args.file)
    if args.interpret:
        try:
            run_file(file)
        except InterpreterSyntaxError as e:
            sys.exit(f"Syntax Error in '{e.source_location.file.name}' at line {e.source_location.line}: {e.message}")
        except InterpreterRuntimeError as e:
            sys.exit(f"Runtime Error in '{e.source_location.file.name}' at line {e.source_location.line}: {e.message}")
        except InterpreterIncludeError as e:
            sys.exit(f"Include Error in '{e.source_location.file.name}' at line {e.source_location.line}: {e.message}")
        except InterpreterFileNotFoundError as e:
            sys.exit(f"File '{e.source_location.file.name}' not found.")
    if args.compile:
        try:
            compile_file_to_c(file)
        except InterpreterSyntaxError as e:
            sys.exit(f"Syntax Error in '{e.source_location.file.name}' at line {e.source_location.line}: {e.message}")
        except InterpreterIncludeError as e:
            sys.exit(f"Include Error in '{e.source_location.file.name}' at line {e.source_location.line}: {e.message}")
        except InterpreterFileNotFoundError as e:
            sys.exit(f"File '{e.source_location.file.name}' not found.")