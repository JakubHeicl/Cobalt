
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>

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

int main() {
    Stack stack;
    stack_init(&stack, 128);
    double variables[1];
    bool initialized_variables[1] = {false};                     
    const char *strings[6] = {"ENTER A NUMBER", "ENTER A SECOND NUMBER", "CHOOSE AN OPERATION + (1), - (2), * (3), / (4), % (5)", "I DO NOT KNOW THIS OPERATION", "RESULT:", "DO YOU WANNA START AGAIN? YES (1), NO (0)"};
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

    printf("%s\n", strings[1]);

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

    variables[0] = pop(&stack);
    initialized_variables[0] = true;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    push(&stack, 1);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    a = pop(&stack);
    if(a == 0.0) goto A;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    push(&stack, 2);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    a = pop(&stack);
    if(a == 0.0) goto B;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    push(&stack, 3);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    a = pop(&stack);
    if(a == 0.0) goto C;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    push(&stack, 4);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    a = pop(&stack);
    if(a == 0.0) goto D;

    if(!initialized_variables[0]) {
        fprintf(stderr, "Variable is not initialized!");
        exit(1);
    }
    push(&stack, variables[0]);

    push(&stack, 5);

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    a = pop(&stack);
    if(a == 0.0) goto E;

    printf("%s\n", strings[3]);

    goto L1;

    A:

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, b + a);

    printf("%s\n", strings[4]);

    printf("%f\n", peek(&stack));

    goto L1;

    B:

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a - b);

    printf("%s\n", strings[4]);

    printf("%f\n", peek(&stack));

    goto L1;

    C:

    b = pop(&stack);
    a = pop(&stack);
    push(&stack, a * b);

    printf("%s\n", strings[4]);

    printf("%f\n", peek(&stack));

    goto L1;

    D:

    b = pop(&stack);
    a = pop(&stack);
    if(b == 0.0) {
        fprintf(stderr, "Division by zero");
        exit(1);
    }
    push(&stack, a / b);

    printf("%s\n", strings[4]);

    printf("%f\n", peek(&stack));

    goto L1;

    E:

    b = pop(&stack);
    a = pop(&stack);
    if(b == 0.0) {
        fprintf(stderr, "Modulo by zero");
        exit(1);
    }
    push(&stack, fmod(a, b));

    printf("%s\n", strings[4]);

    printf("%f\n", peek(&stack));

    goto L1;

    L1:

    printf("%s\n", strings[5]);

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
