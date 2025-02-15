
// sequence of bytecode
// hence named chunk
#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"
#include "value.h"

// OP_CONSTANT -> 2 bytes long: one for opcode and other for operand
// OP_RETRURN -> 1 byte long
typedef enum
{
    OP_CONSTANT, // load constant value in VM's stack
    OP_RETURN,   // instruction will return from current function
} OpCode;        // Opcode -> Operation code

typedef struct
{
    int capacity;         //  size of the array
    int count;            //  no. of elements in the array
    uint8_t *code;        // point to an array which is dynamic
    ValueArray constants; // stores the constants
} Chunk;                  // holds the data along with instruction

void initChunk(Chunk *chunk);                // initialising mem chunk
void freeChunk(Chunk *chunk);                // free the memory allocated to prev chunk
void writeChunk(Chunk *chunk, uint8_t byte); // appending a byte to end of array 'chunk'
int addConstant(Chunk *chunk, Value value);  // appends constant to ValueArray or constant array

#endif