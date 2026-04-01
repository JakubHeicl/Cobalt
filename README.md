# Cobalt

Cobalt is a small stack-based language created as a learning project. This repository contains two implementations of the same interpreter:

- a Python implementation packaged in `python/cobalt`
- a C implementation in `c/`

The repository also includes example `.co` programs and an archived older Python version.

## Project Structure

```text
cobalt/
├─ c/
│  └─ interpreter.c
├─ example_programs/
│  ├─ calculator.co
│  ├─ countdown.co
│  ├─ factorial.co
│  ├─ isprime.co
│  ├─ parity.co
│  └─ sumton.co
├─ legacy/
│  └─ interpreter_v1.py
├─ python/
│  ├─ cobalt/
│  │  ├─ __init__.py
│  │  ├─ __main__.py
│  │  ├─ instructions.py
│  │  ├─ interpreter.py
│  │  ├─ interpreter_errors.py
│  │  └─ stack.py
├─ pyproject.toml
└─ README.md
```

## Python Implementation

Install the package in editable mode from the repository root:

```bash
python -m pip install -e .
```

Run a program like this:

```bash
python -m cobalt example_programs/factorial.co
```

Another example:

```bash
python -m cobalt example_programs/parity.co
```

If you get `No module named cobalt`, the package usually has not been installed yet with `pip install -e .`.

## C Implementation

The C version is stored in `c/interpreter.c`.

Example compilation with Clang:

```bash
clang c/interpreter.c -o c/interpreter.exe
```

Run it like this:

```bash
c/interpreter.exe example_programs/factorial.co
```

## Language Overview

Cobalt is a stack-based language. Most instructions work by popping values from the stack, performing an operation, and pushing a result back.

The language currently supports:

- numbers
- labels
- variables
- string literals for `PRC`
- conditional and unconditional jumps
- configurable stack size through `STK`

### Lexical and Syntax Rules

- Commands are written as uppercase mnemonics such as `PUS`, `ADD`, `JUM`, or `STP`.
- Tokens are separated by whitespace.
- Empty lines are ignored.
- Comments start with `#` and continue until the end of the line.
- Labels end with `:`.
- Strings must be written inside double quotes.
- Identifiers are used for variable names and jump targets.
- In practice, most programs use one instruction per line, but the parser works on whitespace-separated tokens.

Example:

```text
STK 128

START:
PRC "ENTER A NUMBER:"
REA
SET N
PUS 1
SET RES
```

## Values and Arguments

Cobalt is numerically focused. All runtime numeric values on the stack are stored as floating-point values, even when the source literal looks like an integer.

The parser currently distinguishes these token kinds:

- command
- positive integer
- floating-point number
- identifier
- string
- label

From the language user's point of view, the important rule is simply:

- `STK` expects a positive integer literal
- `PUS` expects a numeric literal
- `PRC` expects a string literal
- `GET`, `SET`, `JUM`, `JIZ`, and `JIT` expect an identifier

Examples:

```text
STK 128
PUS 5
PUS 3.14
PUS -2
PRC "HELLO"
GET COUNT
JUM LOOP
```

## Execution Model

Execution starts at the first compiled instruction and proceeds through the instruction list using a program counter.

Some instructions only move to the next instruction:

- `PUS`
- arithmetic instructions
- comparison instructions
- `GET`
- `SET`
- `PRC`
- `PRM`

Some instructions change control flow:

- `JUM` jumps unconditionally
- `JIZ` jumps when the popped value is `0`
- `JIT` jumps when the popped value is `1`
- `STP` ends the program

If an instruction cannot complete correctly, the interpreter raises a runtime error. Typical examples are:

- stack underflow
- division by zero
- modulo by zero
- invalid boolean values for `AND`, `OR`, `NOT`, or `JIT`
- reading a variable before it has been initialized

## Stack Model

The stack is the core runtime structure.

- `PUS` pushes a value onto the stack
- arithmetic, comparison, and boolean operations usually pop two values
- `PRM` prints the current top value without removing it
- `POP` removes the top value
- `DUP` duplicates the top value
- `SWP` swaps the top two values

If an operation requires values that are not present, the interpreter raises a runtime error.

## Variables

Variables are referenced by name through `SET` and `GET`.

Current behavior:

- a variable slot is created when the parser first sees that name in `GET` or `SET`
- `SET name` pops a value from the stack and stores it in the variable
- `GET name` pushes the current value of the variable onto the stack
- using `GET` before the variable has been initialized by `SET` causes a runtime error

Example:

```text
REA
SET N
GET N
PRM
```

## Labels and Control Flow

Labels mark instruction positions and are used as jump targets.

Example:

```text
LOOP:
GET N
JIZ END
...
JUM LOOP

END:
STP
```

Rules:

- labels must be unique
- jump targets must exist
- `JIZ` and `JIT` consume the value they test from the stack

## `STK` Directive

`STK` configures the stack size for the current program.

Rules:

- `STK` must be the first command in the file
- it expects a positive integer
- if `STK` is not present, the default stack size is `64`

Example:

```text
STK 256
```

## Instruction Reference

### Input and Output

`REA`
: Syntax: `REA`
: Reads one line from standard input, converts it to a number, and pushes it onto the stack.

`PRC "text"`
: Syntax: `PRC "text"`
: Prints a string literal stored in the program.

`PRM`
: Syntax: `PRM`
: Prints the current top of the stack without removing it.

### Stack Operations

`PUS number`
: Syntax: `PUS number`
: Pushes a numeric literal onto the stack.

`POP`
: Syntax: `POP`
: Removes the top value from the stack.

`DUP`
: Syntax: `DUP`
: Duplicates the top value on the stack.

`SWP`
: Syntax: `SWP`
: Swaps the top two stack values.

### Arithmetic

All arithmetic operations pop two operands in this order:

- first pop -> right operand
- second pop -> left operand

Then they push the result.

`ADD`
: Syntax: `ADD`
: Pops `b`, then `a`, and pushes `a + b`.

`SUB`
: Syntax: `SUB`
: Pops `b`, then `a`, and pushes `a - b`.

`MUL`
: Syntax: `MUL`
: Pops `b`, then `a`, and pushes `a * b`.

`DIV`
: Syntax: `DIV`
: Pops `b`, then `a`, and pushes `a / b`. Division by zero raises a runtime error.

`MOD`
: Syntax: `MOD`
: Pops `b`, then `a`, and pushes `a % b`. Modulo by zero raises a runtime error.

### Comparison

Comparison operations pop two values and push:

- `1` if the comparison is true
- `0` if the comparison is false

`EQU`
: Syntax: `EQU`
: Pops two values and pushes `1` if `a == b`, otherwise `0`.

`NEQ`
: Syntax: `NEQ`
: Pops two values and pushes `1` if `a != b`, otherwise `0`.

`GTH`
: Syntax: `GTH`
: Pops two values and pushes `1` if `a > b`, otherwise `0`.

`LTH`
: Syntax: `LTH`
: Pops two values and pushes `1` if `a < b`, otherwise `0`.

`GEQ`
: Syntax: `GEQ`
: Pops two values and pushes `1` if `a >= b`, otherwise `0`.

`LEQ`
: Syntax: `LEQ`
: Pops two values and pushes `1` if `a <= b`, otherwise `0`.

### Boolean Logic

Boolean instructions expect values `0` or `1`.

`AND`
: Syntax: `AND`
: Pops two boolean values and pushes their logical conjunction.

`OR`
: Syntax: `OR`
: Pops two boolean values and pushes their logical disjunction.

`NOT`
: Syntax: `NOT`
: Pops one boolean value and pushes its negation.

### Variables

`SET name`
: Syntax: `SET name`
: Pops the top stack value and stores it in variable `name`.

`GET name`
: Syntax: `GET name`
: Pushes the value of variable `name` onto the stack. If the variable has not been initialized yet, the interpreter raises a runtime error.

### Control Flow

`JUM label`
: Syntax: `JUM label`
: Unconditional jump to `label`.

`JIZ label`
: Syntax: `JIZ label`
: Pops one value. If it is `0`, jumps to `label`. Otherwise execution continues with the next instruction.

`JIT label`
: Syntax: `JIT label`
: Pops one value. If it is `1`, jumps to `label`. If it is `0`, execution continues. Any other value causes a runtime error.

### Program Configuration and Termination

`STK size`
: Syntax: `STK size`
: Sets the stack size for the program. Must appear as the first command.

`STP`
: Syntax: `STP`
: Stops program execution.

## Example Programs

The `example_programs/` directory currently contains:

- `factorial.co` - factorial computation
- `countdown.co` - a countdown loop
- `parity.co` - even/odd check
- `isprime.co` - primality test
- `calculator.co` - a simple calculator-style program
- `sumton.co` - summation from `1` to `n`

These files also serve as practical smoke tests for the language.

## Version Note

The current main Python implementation is located in `python/cobalt/`.

The older Python version is archived in:

```text
legacy/interpreter_v1.py
```
