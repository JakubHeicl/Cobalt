from .ir import Opcode
from string import Template

INCLUDES = """
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>
"""

STACK_CODE = """
typedef struct {
    int size;
    int sp;
    double *mem;
} Stack;

void stack_init(Stack *stack, int size) {

    stack->size = size;
    stack->sp = -1;
    stack->mem = malloc(size*sizeof(double));

    if(stack->mem == NULL) {
        fprintf(stderr, "Memory allocation failed");
        exit(1);
    }
}

void free_stack(Stack *stack) {

    free(stack->mem);
    stack->sp = -1;
    stack->size = 0;
    stack->mem = NULL;
}

void push(Stack *stack, double number) {

    if(stack->sp + 1 >= stack->size) {
        fprintf(stderr, "Stack overflow");
        exit(1);
    }

    stack->sp += 1;
    stack->mem[stack->sp] = number;
}

double pop(Stack *stack) {

    if(stack->sp < 0) {
        fprintf(stderr, "Stack underflow");
        exit(1);
    }
    double value = stack->mem[stack->sp];
    stack->sp -= 1;
    return value;
}

void duplicate(Stack *stack) {

    if(stack->sp < 0) {
        fprintf(stderr, "An empty stack cannot use the duplicate method");
        exit(1);
    }
    push(stack, stack->mem[stack->sp]);
}

void swap(Stack *stack) {

    if(stack->sp < 1) {
        fprintf(stderr, "A stack containing one or no value cannot use the swap method");
        exit(1);
    }
    double up = stack->mem[stack->sp];
    double down = stack->mem[stack->sp-1];
    stack->mem[stack->sp] = down;
    stack->mem[stack->sp-1] = up;
}

void negate(Stack *stack) {

    if(stack->sp <0) {
        fprintf(stderr, "An empty stack cannot use the negate method");
        exit(1);
    }
    double number = pop(stack);
    number *= -1;
    push(stack, number);
}

int depth(Stack *stack) {
    return stack->sp + 1;
}

double peek(Stack *stack) {

    if(stack->sp < 0) {
        fprintf(stderr, "An empty stack cannot be read");
        exit(1);
    }
    return stack->mem[stack->sp];
}
"""

HELPER_FUNCTIONS = """
void trim_right_whitespace(char *string) {
    size_t len = strlen(string);

    while(len > 0 && isspace((unsigned char) string[len-1])) {
        string[len-1] = '\\0';
        len--;
    }
}

void trim_left_whitespace(char *string) {
    size_t len = strlen(string);
    size_t start = 0;

    while(start < len && isspace((unsigned char) string[start])) {
        start++;
    }
    if(start == len) {
        string[0] = '\\0';
        return;
    }
    memmove(string, string + start, len - start + 1);
}

void strip(char *string) {
    trim_left_whitespace(string);
    trim_right_whitespace(string);   
}
"""

MAIN_FUNCTION = Template("""
int main() {
    Stack stack;
    stack_init(&stack, $stack_size);
    double variables[$n_variables];
    bool initialized_variables[$n_variables] = {false};                     
    const char *strings[$n_strings] = {$strings};
    char line[64];
    char *end;
    double value;
    double a;
    double b;
""")

LABEL = Template("""
    $value:
""")

REA = Template("""
    if(fgets(line, sizeof(line), stdin) == NULL) {
        fprintf(stderr, "Cannot read input");
        exit(1);
    }
    strip(line);
    value = strtod(line, &end);
    if(end == line || *end != '\\0') {
        fprintf(stderr, "Cannot load %s into the stack!", line);
        exit(1);
    }
    push($stack, value);
""")
STP = Template("""
    exit(0);
""")
PRC = Template("""
    printf("%s\\n", strings[$value]);
""")
PRM = Template("""
    printf("%f\\n", peek($stack));
""")
ADD = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, b + a);
""")
SUB = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a - b);
""")
DIV = Template("""
    b = pop($stack);
    a = pop($stack);
    if(b == 0.0) {
        fprintf(stderr, "Division by zero");
        exit(1);
    }
    push($stack, a / b);
""")
MUL = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a * b);
""")
MOD = Template("""
    b = pop($stack);
    a = pop($stack);
    if(b == 0.0) {
        fprintf(stderr, "Modulo by zero");
        exit(1);
    }
    push($stack, fmod(a, b));
""")
JIZ = Template("""
    a = pop($stack);
    if(a == 0.0) goto $value;
""")
JUM = Template("""
    goto $value;
""")
JIT = Template("""
    a = pop($stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for JIT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    if(a != 0.0) goto $value;
""")
PUS = Template("""
    push($stack, $value);
""")
POP = Template("""
    pop($stack);
""")
DUP = Template("""
    duplicate($stack);
""")
SWP = Template("""
    swap($stack);
""")
EQU = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a == b ? 1 : 0);
""")
NEQ = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a != b ? 1 : 0);
""")
GTH = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a > b ? 1 : 0);
""")
LTH = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a < b ? 1 : 0);
""")
GEQ = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a >= b ? 1 : 0);
""")
LEQ = Template("""
    b = pop($stack);
    a = pop($stack);
    push($stack, a <= b ? 1 : 0);
""")
AND = Template("""
    b = pop($stack);
    a = pop($stack);
    if((a != 0.0 && a != 1.0) || (b != 0.0 && b != 1.0)) {
        fprintf(stderr, "Invalid operands for AND. Expected 0 or 1 but got %f and %f", a, b);
        exit(1);
    }
    push($stack, a && b ? 1 : 0);
""")
NOT = Template("""
    a = pop($stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for NOT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    push($stack, !a ? 1 : 0);
""")
OR =  Template("""
    b = pop($stack);
    a = pop($stack);
    if((a != 0.0 && a != 1.0) || (b != 0.0 && b != 1.0)) {
        fprintf(stderr, "Invalid operands for OR. Expected 0 or 1 but got %f and %f", a, b);
        exit(1);
    }
    push($stack, a || b ? 1 : 0);
""")
GET = Template("""
    if(!initialized_variables[$value]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push($stack, variables[$value]);
""")
SET = Template("""
    variables[$value] = pop($stack);
    initialized_variables[$value] = true;
""")
STK = Template("""
    // Stack size is determined at compile time and cannot be changed at runtime.
""")
FUN = Template("""
void $value(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           
""")
RET = Template("""
    return;
}
""")
CAL = Template("""
    $value($stack, variables, initialized_variables, strings);
""")
DEP = Template("""
    push($stack, depth($stack));
""")

OPCODE_TO_CODE = {
    Opcode.REA: REA,
    Opcode.STP: STP,
    Opcode.PRC: PRC,
    Opcode.PRM: PRM,
    Opcode.ADD: ADD,
    Opcode.SUB: SUB, 
    Opcode.DIV: DIV,
    Opcode.MUL: MUL,
    Opcode.MOD: MOD,
    Opcode.JIZ: JIZ,
    Opcode.JUM: JUM,
    Opcode.JIT: JIT,
    Opcode.PUS: PUS,
    Opcode.POP: POP,
    Opcode.DUP: DUP,
    Opcode.SWP: SWP,
    Opcode.FUN: FUN,
    Opcode.RET: RET,
    Opcode.EQU: EQU,
    Opcode.NEQ: NEQ,
    Opcode.GTH: GTH,
    Opcode.LTH: LTH,
    Opcode.GEQ: GEQ,
    Opcode.LEQ: LEQ,
    Opcode.AND: AND,
    Opcode.NOT: NOT,
    Opcode.OR: OR,
    Opcode.GET: GET,
    Opcode.SET: SET,
    Opcode.STK: STK,
    Opcode.CAL: CAL,
    Opcode.DEP: DEP
}