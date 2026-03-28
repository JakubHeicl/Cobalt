from pathlib import Path

class Stack:
    def __init__(self, size = 64):
        self.size = size
        self.sp = -1
        self.mem = [0 for _ in range(size)]

    def push(self, number: float) -> None:
        if self.sp + 1 >= self.size:
            raise RuntimeError("Stack overflow")
        self.sp += 1
        self.mem[self.sp] = number

    def pop(self) -> float:
        if self.sp < 0:
            raise RuntimeError("Stack underflow")
        value = self.mem[self.sp]
        self.sp -= 1
        return value
    
    def duplicate(self):
        if self.sp < 0:
            raise RuntimeError("Cannot duplicate an empty stack")
        self.push(self.mem[self.sp])

    def swap(self):
        if self.sp < 1:
            raise RuntimeError("Cannot swap a stack containg only one or no value")
        up = self.mem[self.sp]
        down = self.mem[self.sp-1]
        self.mem[self.sp] = down
        self.mem[self.sp-1] = up

    def negate(self):
        if self.sp < 0:
            raise RuntimeError("Cannot negate an empty stack")
        number = self.pop()
        number *= -1
        self.push(number)
    
    def read(self) -> float:
        if self.sp < 0:
            raise RuntimeError("Cannot read from an empty stack")
        return self.mem[self.sp]

keywords = {"REA", "STP", "PRC", "PRM",
             "ADD", "SUB", "DIV", "MUL", "MOD",
             "JIZ", "JUM", "JIT",
             "PUS", "POP", "DUP", "SWP",
             "EQU", "NEQ", "GTH", "LTH", "GEQ", "LEQ",
             "AND", "NOT", "OR",
             "GET", "SET" 
             }

class Interpreter:
    def __init__(self, filename):
        self.stack = Stack()
        self.file = Path(filename)
        self.program = []
        self.program_counter = 0
        self.labels = {}
        self.variables = {}
        if self.file.suffix != ".co":
            raise RuntimeError("Wrong filename, use file with .co extension instead")

    def run(self):
        self.tokenize()
        self.execute()

    def tokenize(self):
        token_counter = 0
        with open(self.file, "r") as file:
            lines: list[str] = file.readlines()

        for line in lines:
            line = line.strip()
            if line == "" or line.startswith("#"): 
                continue

            tokens = line.split(maxsplit=1)
            command = tokens[0]

            if (command not in keywords) and (not command.endswith(":")): 
                raise RuntimeError(f"Cannot resolve {tokens[0]} token")
            
            if command.endswith(":"):
                if command[:-1] in self.labels:
                    raise RuntimeError(f"Duplicate label {command[:-1]}")
                self.labels[command[:-1]] = token_counter
                continue
            
            self.program.append(command)
            token_counter += 1

            if command in {"PUS", "JIZ", "PRC", "JUM", "JIT", "GET", "SET"}:
                if len(tokens) == 1: 
                    raise ValueError(f"You cannot use the {command} keyword alone!")
                if command == "PUS":
                    try:
                        float(tokens[1])
                    except ValueError:
                        raise ValueError(f"Cannot push {tokens[1]} into the stack!")
                self.program.append(tokens[1])
                token_counter += 1

        if "STP" not in self.program:
            raise RuntimeError("Program does not contain STP")

    def execute(self):
        while True:
            if not (0 <= self.program_counter < len(self.program)):
                raise RuntimeError("Program counter out of range or missing STP")
            if self.program[self.program_counter] == "STP":
                break
            current_token = self.program[self.program_counter]

            match current_token:
                case "REA":
                    self.stack.push(float(input()))
                case "PUS":
                    next_token = self.program[self.program_counter+1]
                    self.stack.push(float(next_token))
                    self.program_counter += 1
                case "POP":
                    self.stack.pop()
                case "SWP":
                    self.stack.swap()
                case "DUP":
                    self.stack.duplicate()
                case "EQU":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n1 == n2: self.stack.push(1)
                    else: self.stack.push(0)
                case "NEQ":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n1 != n2: self.stack.push(1)
                    else: self.stack.push(0)
                case "GTH":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n2 > n1: self.stack.push(1)
                    else: self.stack.push(0)
                case "LTH":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n2 < n1: self.stack.push(1)
                    else: self.stack.push(0)
                case "GEQ":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n2 >= n1: self.stack.push(1)
                    else: self.stack.push(0)
                case "LEQ":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n2 <= n1: self.stack.push(1)
                    else: self.stack.push(0)
                case "AND":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if (n1 not in [0, 1]) or (n2 not in [0, 1]):
                        raise RuntimeError("Cannot perform boolean logic with non-boolean variables")
                    self.stack.push(n1 and n2)
                case "OR":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if (n1 not in [0, 1]) or (n2 not in [0, 1]):
                        raise RuntimeError("Cannot perform boolean logic with non-boolean variables")
                    self.stack.push(n1 or n2)
                case "NOT":
                    n = self.stack.pop()
                    if n not in [0, 1]:
                        raise RuntimeError("Cannot perform boolean logic with non-boolean variables")
                    self.stack.push(0 if n else 1)
                case "ADD":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    self.stack.push(n1+n2)
                case "SUB":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    self.stack.push(n2-n1)
                case "MUL":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    self.stack.push(n1*n2)
                case "DIV":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n1 == 0:
                        raise RuntimeError("Division by zero")
                    self.stack.push(n2/n1)
                case "MOD":
                    n1 = self.stack.pop()
                    n2 = self.stack.pop()
                    if n1 == 0:
                        raise RuntimeError("Modulo by zero")
                    self.stack.push(n2%n1)
                case "JIZ":
                    number = self.stack.pop()
                    if number == 0:
                        next_token = self.program[self.program_counter+1]
                        if next_token not in self.labels:
                            raise RuntimeError(f"Label {next_token} is invalid!")
                        self.program_counter = self.labels[next_token] - 1
                    else:
                        self.program_counter += 1
                case "JIT":
                    number = self.stack.pop()
                    if number == 1:
                        next_token = self.program[self.program_counter+1]
                        if next_token not in self.labels:
                            raise RuntimeError(f"Label {next_token} is invalid!")
                        self.program_counter = self.labels[next_token] - 1
                    else:
                        self.program_counter += 1
                case "JUM":
                    next_token = self.program[self.program_counter+1]
                    if next_token not in self.labels:
                            raise RuntimeError(f"Label {next_token} is invalid!")
                    self.program_counter = self.labels[next_token] - 1
                case "PRC":
                    next_token = self.program[self.program_counter+1]
                    print(next_token)
                    self.program_counter += 1
                case "PRM":
                    number = self.stack.read()
                    print(number)
                case "SET":
                    number = self.stack.pop()
                    next_token = self.program[self.program_counter+1]
                    self.variables[next_token] = number
                    self.program_counter += 1
                case "GET":
                    next_token = self.program[self.program_counter+1]
                    if next_token not in self.variables:
                        raise ValueError(f"Variable {next_token} is not defined")
                    value = self.variables[next_token]
                    self.stack.push(value)
                    self.program_counter += 1

            self.program_counter += 1

        print(f"Program {self.file} terminated successfully")

if __name__ == "__main__":
    filename = Path("programs", "factorial.co")
    interpreter = Interpreter(filename)
    interpreter.run()