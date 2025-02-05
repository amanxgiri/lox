
// sequence of bytecode
// hence named chunk
#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"

typedef enum
{
    OP_RETURN, // instruction will return from current function
} OpCode;      // Opcode -> Operation code

typedef struct
{
    int count;     //  no. of elements in the array
    int capacity;  //  size of the array
    uint8_t *code; // point to an array which is dynamic
} Chunk;           // holds the data along with instruction

void initChunk(Chunk *chunk); // initialising mem chunk
void freeChunk(Chunk *chunk);
void writeChunk(Chunk *chunk, uint8_t byte); // appending a byte to end of array 'chunk'

#endif