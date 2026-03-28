# Cobalt

Cobalt is a small stack-based interpreted language created as a learning project.
This repository contains two implementations of the interpreter:

- `interpreter.py` - a reference implementation in Python
- `interpreter.c` - a lower-level implementation in C

The project is focused on learning language design, tokenization, execution flow and basic runtime architecture.

## Features

- Stack-based execution model
- Arithmetic operations: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`
- Comparison operations: `EQU`, `NEQ`, `GTH`, `LTH`, `GEQ`, `LEQ`
- Boolean operations: `AND`, `OR`, `NOT`
- Stack operations: `PUS`, `POP`, `DUP`, `SWP`
- Variables: `SET`, `GET`
- Control flow: `JUM`, `JIZ`, `JIT`
- Labels using `LABEL:`
- Input and output using `REA`, `PRC`, `PRM`
- Example `.co` programs included in `programs/`

## Project Structure

```text
cobalt/
|- interpreter.py
|- interpreter.c
|- programs/
|  |- calculator.co
|  |- countdown.co
|  |- factorial.co
|  |- isprime.co
|  |- parity.co
```

## Language Basics

Each instruction is written on its own line.

- Empty lines are ignored
- Lines starting with `#` are treated as comments
- Labels end with `:`
- Some instructions take an argument on the same line

Example:

```text
START:
PRC Enter a number:
REA
SET N
PUS 1
SET RES
```

## Example Program

Example factorial program:

```text
START:
PRC ENTER A NUMBER:
REA
SET N
PUS 1
SET RES

LOOP:
GET N
JIZ RESULT
GET N
GET RES
MUL
SET RES
GET N
PUS 1
SUB
SET N
JUM LOOP

RESULT:
PRC THE RESULT IS:
GET RES
PRM
STP
```

## Running the Python Interpreter

Run:

```bash
python interpreter.py
```

The current Python entry point runs one of the example programs from the
`programs/` directory. You can change the selected file in the `__main__`
section of `interpreter.py`.

## Building and Running the C Interpreter

You need a C compiler such as Clang, GCC, or MSVC.

Example with Clang:

```bash
clang interpreter.c -o interpreter.exe
interpreter.exe programs/factorial.co
```

The C interpreter expects the path to a `.co` program as a command-line argument.

## Example Programs

The `programs/` directory currently contains:

- `factorial.co` - factorial using variables, loops, and jumps
- `countdown.co` - simple countdown loop
- `parity.co` - parity check
- `isprime.co` - primality test
- `calculator.co` - calculator-style program

These files also serve as small regression tests for the language.
