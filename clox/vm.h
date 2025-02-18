
#ifndef clox_vm_h
#define clox_vm_h

#include "chunk.h"

// stores the state that vm need to keep
// track of
typedef struct
{
    Chunk *chunk;
    uint8_t *ip; // ip -> instruction pointer : points to
                 // next instruction that's about to be executed
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

#endif