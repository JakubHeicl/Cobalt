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
│  └─ parity.co
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

## Language Basics

Each instruction is written on its own line.

- empty lines are ignored
- comments start with `#`
- labels end with `:`
- some instructions expect an argument
- strings are expected to be inside `"`

Example:

```text
START:
PRC "ENTER A NUMBER:"
REA
SET N
PUS 1
SET RES
```

## Supported Instructions

- arithmetic: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`
- comparisons: `EQU`, `NEQ`, `GTH`, `LTH`, `GEQ`, `LEQ`
- boolean logic: `AND`, `OR`, `NOT`
- stack operations: `PUS`, `POP`, `DUP`, `SWP`
- variables: `SET`, `GET`
- control flow: `JUM`, `JIZ`, `JIT`
- input and output: `REA`, `PRC`, `PRM`
- program termination: `STP`

## Python Implementation

The Python version is organized as a package. First install it in editable mode from the repository root:

```bash
python -m pip install -e .
```

Then run the interpreter like this:

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

You can use the same approach for the other programs in `example_programs/`.

## Example Programs

The `example_programs/` directory currently contains:

- `factorial.co` - factorial computation
- `countdown.co` - a simple countdown loop
- `parity.co` - even/odd check
- `isprime.co` - primality test
- `calculator.co` - a simple calculator-style program

These files also serve as practical smoke tests for the language.

## Version Note

The current main Python implementation is located in `python/cobalt/`.

The older Python version is archived in:

```text
legacy/interpreter_v1.py
```
