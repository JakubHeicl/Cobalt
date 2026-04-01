class ExecutionError(Exception):
    def __init__(self, message: str):
        self.message = message

class InterpreterSyntaxError(Exception):
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line

class InterpreterRuntimeError(Exception):
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line