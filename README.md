# Cobalt

Cobalt is a small stack-based programming language and interpreter written as a
learning project. The current implementation lives in `python/cobalt` and can
either interpret `.co` programs directly or compile them to C.

The repository also contains example Cobalt programs, generated C examples, a
minimal VS Code syntax-highlighting extension, and older archived
implementations under `legacy/`.

## Quick Start

Install the package in editable mode from the repository root:

```bash
python -m pip install -e .
```

Run a Cobalt program with the interpreter:

```bash
python -m cobalt example_programs/factorial.co --interpret
```

Compile a Cobalt program to C:

```bash
python -m cobalt example_programs/math_demo.co --compile
```

The compiler writes the generated file next to the source file. For example,
`example_programs/math_demo.co` becomes `example_programs/math_demo.c`.

If you do not want to install the package, run it with `PYTHONPATH` pointed at
the `python` directory:

```powershell
$env:PYTHONPATH = "python"
python -m cobalt example_programs/factorial.co --interpret
```

## Requirements

- Python 3.10 or newer
- `numpy`
- optional: a C compiler such as Clang or GCC for generated C files

The Python dependency is declared in `pyproject.toml` and is installed by
`python -m pip install -e .`.

## Command Line Interface

```text
python -m cobalt <file.co> --interpret
python -m cobalt <file.co> --compile
```

Arguments:

- `<file.co>`: path to a Cobalt source file
- `--interpret`: tokenize, preprocess, parse, build, and execute the program
- `--compile`: tokenize, preprocess, parse, and emit a `.c` file

One mode flag is required. If both flags are provided, the program is interpreted
first and then compiled.

The CLI reports syntax, runtime, include, and missing-file errors with the source
file and line number when available.

## Project Structure

```text
cobalt/
|-- example_programs/
|   |-- *.co                 Example Cobalt programs
|   |-- calculator.c         Generated C example
|   `-- sine.c               Generated C example
|-- legacy/
|   |-- c/                   Archived C interpreter
|   |-- cobalt_v2/           Archived Python implementation
|   `-- interpreter_v1.py    Older single-file interpreter
|-- python/
|   `-- cobalt/
|       |-- __main__.py      CLI entry point
|       |-- tokenizer.py     Source tokenizer
|       |-- preprocessor.py  Include expansion
|       |-- parser.py        Syntax validation and symbol collection
|       |-- ir.py            Tokens, statements, opcodes, and program IR
|       |-- interpreter.py   Program builder and Python executor
|       |-- runtime.py       Runtime opcode implementations
|       |-- stack.py         Memory and call stacks
|       |-- compiler.py      C code generator
|       |-- c_templates.py   C templates used by the compiler
|       |-- config.py        Default stack sizes and entry label
|       `-- interpreter_errors.py
|-- vscode/
|   `-- cobalt-language/     VS Code syntax-highlighting extension
|-- pyproject.toml
`-- README.md
```

## Language Model

Cobalt is stack based. Instructions usually read values from the memory stack,
perform an operation, and push a result back.

Runtime numeric values are stored as `float64` values in the Python
implementation. Integer-looking literals are therefore printed as floats by
`PRM`, for example `120.0`.

The runtime has two stacks:

- memory stack: holds program values, default size `128`
- call stack: holds function return addresses in the Python interpreter,
  default size `64`

`STK size` can change the memory stack size for a program. It must be the first
command after include expansion.

## Source Format

- Opcodes are uppercase mnemonics such as `PUS`, `ADD`, `JUM`, and `STP`.
- Tokens are separated by whitespace.
- Empty lines are ignored.
- Comments start with `#` and continue to the end of the line.
- Labels are identifiers followed by `:`.
- Strings are written in double quotes.
- Most examples use one instruction per line, but multiple instructions can be
  written on one line.
- Negative numeric literals are accepted for numeric operands such as `PUS -1`.

Example:

```text
START:
PRC "ENTER A NUMBER:"
REA
SET N
PUS 1
SET RESULT
STP
```

## Program Structure

Every current Cobalt program must include the entry label:

```text
START:
```

Execution starts at `START`, not necessarily at the first line of the file. This
allows function definitions to appear before the main program.

The program must also contain `STP` in the main program. `STP` stops execution.

Labels must be unique. Jumps are scoped: a jump inside a function can only target
a label in that same function, and a jump in the main program can only target a
label in the main program.

## Includes

`ICL "file.co"` includes another source file before parsing.

```text
ICL "math.co"

START:
PUS -10
CAL ABS
PRM
STP
```

Included paths are resolved relative to the file that contains the `ICL`
instruction. The preprocessor detects include cycles and skips files that have
already been included.

## Functions

Functions are declared before `START`:

```text
FUN SQUARE
    DUP
    MUL
    RET

START:
    PUS 5
    CAL SQUARE
    PRM
    STP
```

Function rules:

- `FUN name` starts a function definition.
- `RET` returns from the current function.
- `CAL name` calls a function.
- Functions must be defined before `START`.
- Functions cannot be nested.
- Function calls pass data through the shared memory stack.
- Variables are global runtime slots shared by the main program and functions.

## Variables

Variables are created by the parser when their names appear in `GET` or `SET`.

```text
REA
SET N
GET N
PRM
```

Rules:

- `SET name` pops the top value and stores it.
- `GET name` pushes the stored value.
- Reading a variable before it has been initialized raises a runtime error.

## Instruction Reference

### Input and Output

`REA`
: Reads one line from standard input, converts it to a number, and pushes it.

`PRC "text"`
: Prints a string literal.

`PRM`
: Prints the current top value without removing it.

### Stack Operations

`PUS number`
: Pushes a numeric literal.

`POP`
: Removes the top value.

`DUP`
: Duplicates the top value.

`SWP`
: Swaps the top two values.

`DEP`
: Pushes the current memory-stack depth.

### Arithmetic

Arithmetic instructions pop `b` first, then `a`, and push the result.

`ADD`
: Pushes `a + b`.

`SUB`
: Pushes `a - b`.

`MUL`
: Pushes `a * b`.

`DIV`
: Pushes `a / b`. Division by zero raises a runtime error.

`MOD`
: Pushes `a % b`. Modulo by zero raises a runtime error.

### Comparison

Comparison instructions pop `b` first, then `a`, and push `1` for true or `0`
for false.

`EQU`
: `a == b`

`NEQ`
: `a != b`

`GTH`
: `a > b`

`LTH`
: `a < b`

`GEQ`
: `a >= b`

`LEQ`
: `a <= b`

### Boolean Logic

Boolean instructions expect values `0` or `1`.

`AND`
: Logical conjunction.

`OR`
: Logical disjunction.

`NOT`
: Logical negation.

### Variables

`SET name`
: Pops and stores a value.

`GET name`
: Pushes a stored value.

### Control Flow

`JUM label`
: Jumps unconditionally.

`JIZ label`
: Pops a value and jumps if it is `0`.

`JIT label`
: Pops a value and jumps if it is `1`. Values other than `0` or `1` are runtime
errors.

### Functions

`FUN name`
: Declares a function. This is a compile-time declaration and does not execute
at runtime.

`CAL name`
: Calls a function.

`RET`
: Returns from a function.

### Program Configuration and Termination

`ICL "file.co"`
: Includes another source file before parsing.

`STK size`
: Sets the memory stack size. The argument must be a positive integer.

`STP`
: Stops the main program.

## Compiling Generated C

After running `--compile`, compile the generated C file with your system C
compiler.

On Windows with Clang:

```powershell
clang example_programs\math_demo.c -o math_demo.exe
.\math_demo.exe
```

On Unix-like systems, link the math library because generated code uses `fmod`
for `MOD`:

```bash
cc example_programs/math_demo.c -lm -o math_demo
./math_demo
```

Generated C mirrors the Cobalt program with C functions, labels, `goto` jumps,
and a small stack runtime emitted from `python/cobalt/c_templates.py`.

## Example Programs

The `example_programs/` directory includes:

- `calculator.co`: four-operation calculator with modulo
- `countdown.co`: countdown loop
- `factorial.co`: factorial computation
- `fibonacci.co`: Fibonacci computation
- `isprime.co`: primality check
- `math.co`: reusable functions such as `ABS`, `MIN`, `MAX`, and `CLAMP`
- `math_demo.co`: include and function-call demo using `math.co`
- `power.co`: integer power loop
- `sine.co`: sine approximation using functions
- `sumton.co`: iterative sum from `1` to `n`
- `sumton2.co`: direct arithmetic sum formula
- `calculator.c` and `sine.c`: generated C snapshots

Note: `parity.co` is an older example and currently does not include the required
`START:` label, so the current parser rejects it.

## VS Code Extension

`vscode/cobalt-language` contains a minimal local VS Code extension for Cobalt
syntax highlighting.

It provides:

- `.co` file association
- line comments with `#`
- highlighting for opcodes, labels, variables, strings, numbers, includes, and
  function calls

It does not provide diagnostics, snippets, autocomplete, formatting, or run
commands.

To test it locally:

1. Open `vscode/cobalt-language` in VS Code.
2. Press `F5`.
3. Open a `.co` file in the Extension Development Host window.

## Development Notes

The current pipeline is:

```text
source file
-> tokenizer
-> include preprocessor
-> parser and symbol collection
-> Python Program IR
-> interpreter execution or C code generation
```

There is no dedicated automated test suite in this repository yet. The example
programs are the most useful smoke tests for interpreter and compiler behavior.

Useful smoke-test commands:

```bash
python -m cobalt example_programs/factorial.co --interpret
python -m cobalt example_programs/math_demo.co --compile
```

## Troubleshooting

`No module named cobalt`
: Install the project with `python -m pip install -e .`, or set
`PYTHONPATH=python` when running from the repository root.

`Please specify --interpret or --compile.`
: Add one of the required mode flags.

`The program must include the entry label 'START:'`
: Add a `START:` label to the main program.

`Missing STP command to stop the program.`
: Add `STP` to the main program.

`Include cycle detected`
: Check `ICL` usage for files that include each other.
