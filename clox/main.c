
#include "common.h"
#include "chunk.h"
#include "debug.h"

int main(int argc, const char *argv[])
{
    Chunk chunk;
    initChunk(&chunk);

    int constant = addConstant(&chunk, 1.2); // adds to constant pool
    writeChunk(&chunk, OP_CONSTANT);         // Writes opcode
    writeChunk(&chunk, constant);            // Write operand(index)

    writeChunk(&chunk, OP_RETURN);

    disassemble(&chunk, "test_chunk");
    freeChunk(&chunk);
    return 0;
}