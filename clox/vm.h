
#ifndef clox_vm_h
#define clox_vm_h

#include "chunk.h"
#include "value.h"

#define STACK_MAX 256

// stores the state that vm need to keep
// track of
typedef struct
{
    Chunk *chunk;
    uint8_t *ip;            // ip -> instruction pointer : points to
                            // next instruction that's about to be executed
    Value stack[STACK_MAX]; // stack array to store values
                            // hold temp variable , manages func call, stores intermediate value
    Value *stackTop;        // stack pointer -> points after the top element of stack
                            // or it stack top points to where next value to be pushed will
                            // go

} VM;

typedef enum
{
    INTERPRET_OK,            // returns successfull execution and finished
    INTERPRET_COMPILE_ERROR, // Error during parsing/compliling
    INTERPRET_RUNTIME_ERROR, // Error during execution
} InterpretResult;

void initVM();
void freeVM();
InterpretResult interpret(Chunk *chunk);

// Stack operations
void push(Value value); // Adds value to top
Value pop();            // Removes and returns top value

void push(Value value)
{
    *vm.stackTop = value;
    vm.stackTop++;
}

Value pop()
{
    vm.stackTop--;
    return *vm.stackTop;
}

#endif