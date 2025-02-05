
#include <stdlib.h>

#include "memory.h"

// helps in memory management
// allocating memory, freeing it, and
// chaning size of existing allocation
void *reallocate(void *pointer, size_t oldSize, size_t newSize)
{
    if (newSize == 0)
    {
        free(pointer);
        return NULL;
    }

    void *result = realloc(pointer, newSize);
    if (result == NULL)
    {
        exit(1);
    }

    return result;
}