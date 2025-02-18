
#include "stdio.h"

#include "common.h"
#include "vm.h"
#include "debug.h"

// global static vm instance
VM vm;

void initVM() {}

void freeVM() {}

// most important function of The VM
static InterpretResult run()
{
// reads the byte currently pointed by ip and
// advances the pointer
#define READ_BYTE() (*vm.ip++)

#define READ_CONSTANT() (vm.chunk->constants.values[READ_BYTE()])
    for (;;)
    {

#ifdef DEBUG_TRACE_EXECUTION disassembleInstruction(vm.chunk, (int)(vm.ip - vm.chunk->code));

#endif
        uint8_t instruction;
        switch (instruction = READ_BYTE())
        {
        case OP_CONSTANT:
        {
            Value constant = READ_CONSTANT();
            printValue(constant);
            printf("\n");
            break;
        }
        case OP_RETURN:
        {
            return INTERPRET_OK;
        }
        }
    }

#undef READ_BYTE()
#undef READ_CONSTANT()
}

InterpretResult interpret(Chunk *chunk)
{
    vm.chunk = chunk;
    vm.ip = vm.chunk->code; // points to next instruction
    return run();
}