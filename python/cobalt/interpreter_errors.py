from .ir import SourceLocation

class ExecutionError(Exception):
    def __init__(self, message: str):
        self.message = message

class StackError(ExecutionError):
    def __init__(self, message: str):
        super().__init__(message)

class InterpreterSyntaxError(Exception):
    def __init__(self, message: str, source_location: SourceLocation):
        self.message = message
        self.source_location = source_location

class InterpreterRuntimeError(Exception):
    def __init__(self, message: str, source_location: SourceLocation):
        self.message = message
        self.source_location = source_location

class InterpreterFileNotFoundError(Exception):
    def __init__(self, message: str, source_location: SourceLocation):
        self.message = message
        self.source_location = source_location

class InterpreterIncludeError(Exception):
    def __init__(self, message: str, source_location: SourceLocation):
        self.message = message
        self.source_location = source_location