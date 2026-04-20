
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdbool.h>

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

void trim_right_whitespace(char *string) {
    size_t len = strlen(string);

    while(len > 0 && isspace((unsigned char) string[len-1])) {
        string[len-1] = '\0';
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
        string[0] = '\0';
        return;
    }
    memmove(string, string + start, len - start + 1);
}

void strip(char *string) {
    trim_left_whitespace(string);
    trim_right_whitespace(string);   
}

void X_SQUARED(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[0]);

    duplicate(stack);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    return;
}

void TWO_K_TWO(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           

    if(!initialized_variables[1]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[1]);

    push(stack, 2);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    push(stack, 2);

    b = pop(stack);
    a = pop(stack);
    push(stack, b + a);

    return;
}

void TWO_K_THREE(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           

    if(!initialized_variables[1]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[1]);

    push(stack, 2);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    push(stack, 3);

    b = pop(stack);
    a = pop(stack);
    push(stack, b + a);

    return;
}

void NEXT_TERM(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           

    if(!initialized_variables[2]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[2]);

    push(stack, -1.0);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    X_SQUARED(stack, variables, initialized_variables, strings);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    TWO_K_THREE(stack, variables, initialized_variables, strings);

    b = pop(stack);
    a = pop(stack);
    if(b == 0.0) {
        fprintf(stderr, "Division by zero");
        exit(1);
    }
    push(stack, a / b);

    TWO_K_TWO(stack, variables, initialized_variables, strings);

    b = pop(stack);
    a = pop(stack);
    if(b == 0.0) {
        fprintf(stderr, "Division by zero");
        exit(1);
    }
    push(stack, a / b);

    variables[2] = pop(stack);
    initialized_variables[2] = true;

    return;
}

void X_IN_BOUNDS(Stack *stack, double *variables, bool *initialized_variables, const char **strings) {
    char line[64];
    char *end;
    double value;
    double a;
    double b;           

    BEGIN:

    push(stack, 3.14159265358979);

    variables[3] = pop(stack);
    initialized_variables[3] = true;

    if(!initialized_variables[3]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[3]);

    push(stack, 2);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    variables[4] = pop(stack);
    initialized_variables[4] = true;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[0]);

    if(!initialized_variables[3]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[3]);

    b = pop(stack);
    a = pop(stack);
    push(stack, a >= b ? 1 : 0);

    a = pop(stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for JIT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    if(a != 0.0) goto BIGGER;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[0]);

    if(!initialized_variables[3]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[3]);

    push(stack, -1.0);

    b = pop(stack);
    a = pop(stack);
    push(stack, a * b);

    b = pop(stack);
    a = pop(stack);
    push(stack, a <= b ? 1 : 0);

    a = pop(stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for JIT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    if(a != 0.0) goto SMALLER;

    goto END;

    BIGGER:

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[0]);

    if(!initialized_variables[4]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[4]);

    b = pop(stack);
    a = pop(stack);
    push(stack, a - b);

    variables[0] = pop(stack);
    initialized_variables[0] = true;

    goto BEGIN;

    SMALLER:

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[0]);

    if(!initialized_variables[4]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(stack, variables[4]);

    b = pop(stack);
    a = pop(stack);
    push(stack, b + a);

    variables[0] = pop(stack);
    initialized_variables[0] = true;

    goto BEGIN;

    END:

    return;
}

int main() {
    Stack stack;
    stack_init(&stack, 128);
    double variables[7];
    bool initialized_variables[7] = {false};                     
    const char *strings[3] = {"ENTER A NUMBER:\\", "THE RESULT IS:", "DO YOU WANNA START AGAIN? YES (1), NO (0)"};
    char line[64];
    char *end;
    double value;
    double a;
    double b;

    START:

    printf("%s\n", strings[0]);

    if(fgets(line, sizeof(line), stdin) == NULL) {
        fprintf(stderr, "Cannot read input");
        exit(1);
    }
    strip(line);
    value = strtod(line, &end);
    if(end == line || *end != '\0') {
        fprintf(stderr, "Cannot load %s into the stack!", line);
        exit(1);
    }
    push(&stack, value);

    variables[0] = pop(&stack);
    initialized_variables[0] = true;

    X_IN_BOUNDS(&stack, variables, initialized_variables, strings);

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    variables[2] = pop(&stack);
    initialized_variables[2] = true;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    variables[5] = pop(&stack);
    initialized_variables[5] = true;

    push(&stack, 0);

    variables[1] = pop(&stack);
    initialized_variables[1] = true;

    push(&stack, 100);

    variables[6] = pop(&stack);
    initialized_variables[6] = true;

    LOOP:

    if(!initialized_variables[1]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[1]);

    if(!initialized_variables[6]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[6]);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a == b ? 1 : 0);

    a = pop(&stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for JIT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    if(a != 0.0) goto RESULT;

    NEXT_TERM(&stack, variables, initialized_variables, strings);

    if(!initialized_variables[5]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[5]);

    if(!initialized_variables[2]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[2]);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, b + a);

    variables[5] = pop(&stack);
    initialized_variables[5] = true;

    if(!initialized_variables[1]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[1]);

    push(&stack, 1);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, b + a);

    variables[1] = pop(&stack);
    initialized_variables[1] = true;

    goto LOOP;

    RESULT:

    printf("%s\n", strings[1]);

    if(!initialized_variables[5]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[5]);

    printf("%f\n", peek(&stack));

    printf("%s\n", strings[2]);

    if(fgets(line, sizeof(line), stdin) == NULL) {
        fprintf(stderr, "Cannot read input");
        exit(1);
    }
    strip(line);
    value = strtod(line, &end);
    if(end == line || *end != '\0') {
        fprintf(stderr, "Cannot load %s into the stack!", line);
        exit(1);
    }
    push(&stack, value);

    a = pop(&stack);
    if(a != 0.0 && a != 1.0) {
        fprintf(stderr, "Invalid operand for JIT. Expected 0 or 1 but got %f", a);
        exit(1);
    }
    if(a != 0.0) goto START;

    exit(0);
    return 0;
}
