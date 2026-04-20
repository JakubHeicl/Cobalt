#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define CHARS_LINE 256
#define COMMAND_SIZE 3
#define LABEL_SIZE 8
#define VAR_SIZE 8
#define MESSAGE_SIZE 128
#define STACK_SIZE 128

typedef struct {
    int size;
    int sp;
    double *mem;
} Stack;

typedef enum {
    REA, STP, PRC, PRM, ADD, 
    SUB, DIV, MUL, MOD, JIZ, 
    JUM, JIT, PUS, POP, DUP, 
    SWP, EQU, NEQ, GTH, LTH, 
    GEQ, LEQ, AND, NOT, OR, 
    GET, SET
} Command;

typedef enum {
    COMMAND, MESSAGE_INDEX, LABEL_NAME, VAR_NAME, VALUE
} Token_type;

typedef union {
    Command command;
    int message_index;
    char label_name[LABEL_SIZE];
    char var_name[VAR_SIZE];
    double value;
} Token_value;

typedef struct {
    Token_type token_type;
    Token_value token_value;
} Token;

typedef struct {
    double value;
    char name[VAR_SIZE];
} Variable;

typedef struct {
    int token_position;
    char name[LABEL_SIZE];
} Label;

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

double read(Stack *stack) {

    if(stack->sp < 0) {
        fprintf(stderr, "An empty stack cannot be read");
        exit(1);
    }
    return stack->mem[stack->sp];
}

int count_lines(FILE *file) {
    int ch;
    int n_lines = 1;
    while((ch = getc(file)) != EOF) {
        if(ch == '\n') {
            n_lines++;
        }
    }
    rewind(file);
    return n_lines;
}

int ends_with(char *string, char *suffix) {

    int string_len = strlen(string);
    int suffix_len = strlen(suffix);

    if (suffix_len > string_len) {
        return 0;
    }
    return strcmp(string + string_len - suffix_len, suffix) == 0;
}

void chop_right(char *string, size_t n) {
    size_t len = strlen(string);

    if(n >= len) {
        string[0] = '\0';
    }
    else {
        string[len-n] = '\0';
    }
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

void stop_if_empty(char *string) {
    if(strcmp(string, "") == 0) {
        fprintf(stderr, "Missing argument");
        exit(1);
    }
    else return;
}

void set_command(Token *token, Command command) {
    token->token_value.command = command;
    token->token_type = COMMAND;
}

void tokenize_file(FILE *file, Token **tokens, int *token_count, Label **labels, int *label_count, char (**messages)[MESSAGE_SIZE], Variable **variables, int *variables_size) {
    int token_counter = 0;
    int label_counter = 0;
    int message_counter = 0;
    int n_lines = count_lines(file);

    int is_STP = 0;

    char *line = malloc(sizeof(char)*CHARS_LINE);

    size_t labels_size = n_lines;
    size_t tokens_size = 2*n_lines;
    *tokens = malloc(sizeof(Token)*tokens_size);
    *labels = malloc(sizeof(Label)*labels_size);
    *variables = malloc(sizeof(Variable)*n_lines);
    *messages = malloc(sizeof(**messages)*n_lines);

    if(line == NULL || *tokens == NULL || *labels == NULL || *variables == NULL || *messages == NULL) {
        fprintf(stderr, "Memory allocation failed");
        free(line);
        free(*tokens);
        free(*labels);
        free(*variables);
        free(*messages);
        exit(1);
    }

    while(fgets(line, CHARS_LINE, file)) {
        char *p = line;

        while(isspace((unsigned char)*p)) p++;
        if(*p == '\0' || *p == '#' || *p == '\n') continue;

        char first_token[LABEL_SIZE+1];
        int char_count = 0;
        while(*p && !isspace((unsigned char)*p) && (char_count < LABEL_SIZE - 1)) {
            first_token[char_count] = *p;
            p++;
            char_count++;
        }
        first_token[char_count] = '\0';
        while(isspace((unsigned char)*p)) p++;

        char second_token[MESSAGE_SIZE+1];
        char_count = 0;
        while(*p && (char_count < MESSAGE_SIZE - 1) && *p != '\n') {
            second_token[char_count] = *p;
            p++;
            char_count++;
        }
        second_token[char_count] = '\0';
        trim_right_whitespace(second_token);
        
        if(ends_with(first_token, ":")) {
            chop_right(first_token, 1);
            for(int i = 0; i < label_counter; i++) {
                if(strcmp((*labels)[i].name, first_token) == 0) {
                    fprintf(stderr, "Duplicate label %s", first_token);
                    exit(1);
                }
            }
            (*labels)[label_counter].token_position = token_counter;
            strcpy((*labels)[label_counter].name, first_token);
            label_counter++;
            continue;
        }
        if(strcmp(first_token, "STP") == 0) {
            set_command(&(*tokens)[token_counter], STP);
            is_STP = 1;
        } else if(strcmp(first_token, "REA") == 0) set_command(&(*tokens)[token_counter], REA);
        else if(strcmp(first_token, "PRC") == 0) set_command(&(*tokens)[token_counter], PRC);
        else if(strcmp(first_token, "PRM") == 0) set_command(&(*tokens)[token_counter], PRM);
        else if(strcmp(first_token, "ADD") == 0) set_command(&(*tokens)[token_counter], ADD);
        else if(strcmp(first_token, "SUB") == 0) set_command(&(*tokens)[token_counter], SUB);
        else if(strcmp(first_token, "DIV") == 0) set_command(&(*tokens)[token_counter], DIV);
        else if(strcmp(first_token, "MUL") == 0) set_command(&(*tokens)[token_counter], MUL);
        else if(strcmp(first_token, "MOD") == 0) set_command(&(*tokens)[token_counter], MOD);
        else if(strcmp(first_token, "JIZ") == 0) set_command(&(*tokens)[token_counter], JIZ);
        else if(strcmp(first_token, "JUM") == 0) set_command(&(*tokens)[token_counter], JUM);
        else if(strcmp(first_token, "JIT") == 0) set_command(&(*tokens)[token_counter], JIT);
        else if(strcmp(first_token, "PUS") == 0) set_command(&(*tokens)[token_counter], PUS);
        else if(strcmp(first_token, "POP") == 0) set_command(&(*tokens)[token_counter], POP);
        else if(strcmp(first_token, "DUP") == 0) set_command(&(*tokens)[token_counter], DUP);
        else if(strcmp(first_token, "SWP") == 0) set_command(&(*tokens)[token_counter], SWP);
        else if(strcmp(first_token, "EQU") == 0) set_command(&(*tokens)[token_counter], EQU);
        else if(strcmp(first_token, "NEQ") == 0) set_command(&(*tokens)[token_counter], NEQ);
        else if(strcmp(first_token, "GTH") == 0) set_command(&(*tokens)[token_counter], GTH);
        else if(strcmp(first_token, "LTH") == 0) set_command(&(*tokens)[token_counter], LTH);
        else if(strcmp(first_token, "GEQ") == 0) set_command(&(*tokens)[token_counter], GEQ);
        else if(strcmp(first_token, "LEQ") == 0) set_command(&(*tokens)[token_counter], LEQ);
        else if(strcmp(first_token, "AND") == 0) set_command(&(*tokens)[token_counter], AND);
        else if(strcmp(first_token, "NOT") == 0) set_command(&(*tokens)[token_counter], NOT);
        else if(strcmp(first_token, "OR" ) == 0) set_command(&(*tokens)[token_counter], OR);
        else if(strcmp(first_token, "GET") == 0) set_command(&(*tokens)[token_counter], GET);
        else if(strcmp(first_token, "SET") == 0) set_command(&(*tokens)[token_counter], SET);
        else {
            fprintf(stderr, "Cannot resolve %s token", first_token);
            exit(1);
        }
        token_counter++;
        switch ((*tokens)[token_counter - 1].token_value.command) {
            case PUS: {
                stop_if_empty(second_token);
                char *end;
                double value = strtod(second_token, &end);
                if(end == second_token || *end != '\0') {
                    fprintf(stderr, "Cannot push %s into the stack!", second_token);
                    exit(1);
                }
                (*tokens)[token_counter].token_value.value = value;
                (*tokens)[token_counter].token_type = VALUE;
                token_counter++;
                break;
            }
            case JIZ:
            case JUM:
            case JIT:
                stop_if_empty(second_token);
                strcpy((*tokens)[token_counter].token_value.label_name, second_token);
                (*tokens)[token_counter].token_type = LABEL_NAME;
                token_counter++;
                break;
            case PRC:
                stop_if_empty(second_token);
                strcpy((*messages)[message_counter], second_token);
                (*tokens)[token_counter].token_value.message_index = message_counter;
                (*tokens)[token_counter].token_type = MESSAGE_INDEX;
                message_counter++;
                token_counter++;
                break;
            case SET:
            case GET:
                stop_if_empty(second_token);
                strcpy((*tokens)[token_counter].token_value.var_name, second_token);
                (*tokens)[token_counter].token_type = VAR_NAME;
                token_counter++;
                break;
        }        
    }
    free(line);
    if(!is_STP) {
        fprintf(stderr, "Program does not contain STP");
        exit(1);
    }
    *token_count = token_counter;
    *label_count = label_counter;
    *variables_size = n_lines;
}

void execute(Stack *stack, Token *tokens, int token_count, Label *labels, int label_count, char (*messages)[MESSAGE_SIZE], Variable *variables, int variables_size) {

    int program_counter = 0;
    int variable_counter = 0;

    while(1) {
        if(!(0 <= program_counter && program_counter < token_count)) {
            fprintf(stderr, "Program counter out of range or missing STP");
            exit(1);
        }
        if(tokens[program_counter].token_type == COMMAND && tokens[program_counter].token_value.command == STP) {
            break;
        }
        if(tokens[program_counter].token_type != COMMAND) {
            fprintf(stderr, "Invalid token at position %d", program_counter);
            exit(1);
        }

        double n1;
        double n2;
        double number;
        double value;
        char *var_name;
        int var_found;

        switch (tokens[program_counter].token_value.command) {
            case REA: {
                char line[CHARS_LINE];
                if(fgets(line, sizeof(line), stdin) == NULL) {
                    fprintf(stderr, "Cannot read input");
                    exit(1);
                }
                trim_right_whitespace(line);
                char *end;
                double value = strtod(line, &end);
                if(end == line || *end != '\0') {
                    fprintf(stderr, "Cannot load %s into the stack!", line);
                    exit(1);
                }
                push(stack, value);
                break;
            }
            case PUS:
                value = tokens[program_counter+1].token_value.value;
                push(stack, value);
                program_counter++;
                break;
            case POP:
                pop(stack);
                break;
            case SWP:
                swap(stack);
                break;
            case DUP:
                duplicate(stack);
                break;
            case EQU:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n1 == n2) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case NEQ:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n1 != n2) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case GTH:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n2 > n1) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case LTH:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n2 < n1) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case GEQ:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n2 >= n1) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case LEQ:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n2 <= n1) push(stack, 1.0);
                else push(stack, 0.0);
                break;
            case AND:
                n1 = pop(stack);
                n2 = pop(stack);
                if((n1 != 0.0 && n1 != 1.0) || (n2 != 0.0 && n2 != 1.0)) {
                    fprintf(stderr, "Cannot perform boolean logic with non-boolean variables");
                    exit(1);
                }
                push(stack, (double) (n1 && n2));
                break;
            case OR:
                n1 = pop(stack);
                n2 = pop(stack);
                if((n1 != 0.0 && n1 != 1.0) || (n2 != 0.0 && n2 != 1.0)) {
                    fprintf(stderr, "Cannot perform boolean logic with non-boolean variables");
                    exit(1);
                }
                push(stack, (double) (n1 || n2));
                break;
            case NOT:
                number = pop(stack);
                if(number != 0.0 && number != 1.0) {
                    fprintf(stderr, "Cannot perform boolean logic with non-boolean variables");
                    exit(1);
                }
                push(stack, (double) (!number));
                break;
            case ADD:
                n1 = pop(stack);
                n2 = pop(stack);
                push(stack, n1+n2);
                break;
            case SUB:
                n1 = pop(stack);
                n2 = pop(stack);
                push(stack, n2-n1);
                break;
            case MUL:
                n1 = pop(stack);
                n2 = pop(stack);
                push(stack, n1*n2);
                break;
            case DIV:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n1 == 0.0) {
                    fprintf(stderr, "Division by zero");
                    exit(1);
                }
                push(stack, n2/n1);
                break;
            case MOD:
                n1 = pop(stack);
                n2 = pop(stack);
                if(n1 == 0.0) {
                    fprintf(stderr, "Modulo by zero");
                    exit(1);
                }
                push(stack, (double) (((int)n2)%((int)n1)));
                break;
            case JIZ:
                number = pop(stack);
                if(number == 0.0) {
                    char *next_token = tokens[program_counter+1].token_value.label_name;
                    int in_labels = 0;
                    for(int i = 0; i < label_count; i++) {
                        if(strcmp(labels[i].name, next_token) == 0) {
                            program_counter = labels[i].token_position - 1;
                            in_labels = 1;
                            break;
                        }
                    }
                    if(!in_labels) {
                        fprintf(stderr, "Label %s is invalid!", next_token);
                        exit(1);
                    }
                } else program_counter++;
                break;
            case JIT:
                number = pop(stack);
                if(number == 1.0) {
                    char *next_token = tokens[program_counter+1].token_value.label_name;
                    int in_labels = 0;
                    for(int i = 0; i < label_count; i++) {
                        if(strcmp(labels[i].name, next_token) == 0) {
                            program_counter = labels[i].token_position - 1;
                            in_labels = 1;
                            break;
                        }
                    }
                    if(!in_labels) {
                        fprintf(stderr, "Label %s is invalid!", next_token);
                        exit(1);
                    }
                } else program_counter++;
                break;
            case JUM: {
                char *next_token = tokens[program_counter+1].token_value.label_name;
                int in_labels = 0;
                for(int i = 0; i < label_count; i++) {
                    if(strcmp(labels[i].name, next_token) == 0) {
                        program_counter = labels[i].token_position - 1;
                        in_labels = 1;
                        break;
                    }
                }
                if(!in_labels) {
                    fprintf(stderr, "Label %s is invalid!", next_token);
                    exit(1);
                }
                break;
            }
            case PRC: {
                int message_index = tokens[program_counter+1].token_value.message_index;
                char* message = messages[message_index];
                printf("%s\n", message);
                program_counter++;
                break;
            }
            case PRM:
                number = read(stack);
                printf("%f\n", number);
                break;
            case SET:
                number = pop(stack);
                var_name = tokens[program_counter+1].token_value.var_name;
                var_found = 0;
                for(int i = 0; i < variable_counter; i++) {
                    if(strcmp(variables[i].name, var_name) == 0) {
                        variables[i].value = number;
                        var_found = 1;
                        break;
                    }
                }
                if(!var_found) {
                    if(variable_counter >= variables_size) {
                        fprintf(stderr, "Too many variables");
                        exit(1);
                    }
                    variables[variable_counter].value = number;
                    strcpy(variables[variable_counter].name, var_name);
                    variable_counter++;
                }
                program_counter++;
                break;
            case GET:
                var_name = tokens[program_counter+1].token_value.var_name;
                var_found = 0;
                for(int i = 0; i < variable_counter; i++) {
                    if(strcmp(variables[i].name, var_name) == 0) {
                        number = variables[i].value;
                        var_found = 1;
                        break;
                    }
                }
                if(!var_found) {
                    fprintf(stderr, "Variable %s is not defined", var_name);
                    exit(1);
                }
                push(stack, number);
                program_counter++;
                break;
        }
        program_counter++;
    }
    printf("Program terminated successfully");
}

int main(int argc, char *argv[]) {

    if(argc != 2) {
        fprintf(stderr, "Usage: %s <filename>", argv[0]);
        exit(1);
    }

    if(!ends_with(argv[1], ".co")) {
        fprintf(stderr, "Wrong filename, use file with .co extension instead");
        exit(1);
    }

    FILE *file = fopen(argv[1], "r");

    if(file == NULL) {
        fprintf(stderr, "Error: I cannot open this file");
        exit(1);
    }

    Stack stack;
    stack_init(&stack, STACK_SIZE);

    Token *tokens;
    Label *labels;
    Variable *variables;
    int token_count;
    int label_count;
    int variables_size;

    char (*messages)[MESSAGE_SIZE];

    tokenize_file(file, &tokens, &token_count, &labels, &label_count, &messages, &variables, &variables_size);
    fclose(file);
    execute(&stack, tokens, token_count, labels, label_count, messages, variables, variables_size);
    free(tokens);
    free(labels);
    free(messages);
    free(variables);
    free_stack(&stack);
    exit(0);
}
