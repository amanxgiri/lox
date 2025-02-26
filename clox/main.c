#include "common.h"
#include "chunk.h"
#include "debug.h"
#include "vm.h"

int main(int argc, const char *argv[])
{

    initVM(); // starts the vm

    Chunk chunk;
    initChunk(&chunk);

    int constant = addConstant(&chunk, 1.2); // adds to constant pool
    writeChunk(&chunk, OP_CONSTANT, 123);    // Writes opcode
    writeChunk(&chunk, constant, 123);       // Write operand(index)

    constant = addConstant(&chunk, 3.4);
    writeChunk(&chunk, OP_CONSTANT, 123);
    writeChunk(&chunk, constant, 123);

    writeChunk(&chunk, OP_RETURN, 123);
    writeChunk(&chunk, OP_NEGATE, 123);

    disassembleChunk(&chunk, "test_chunk");
    interpret(&chunk);
    freeVM();
    freeChunk(&chunk);
    return 0;
}