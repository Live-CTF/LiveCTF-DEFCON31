#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include "alloc.h"

typedef struct chunkinfo {
    unsigned int free;
    uint64_t size;
    struct chunkinfo* next;
} chunkinfo;

const size_t infoSize = sizeof(chunkinfo);

chunkinfo* HEAD = 0;

void print_state()
{
    size_t i = 0;
    for (chunkinfo* chunk = HEAD; chunk != NULL; chunk = chunk->next)
    {
        printf("Chunk %lu:\n  Addr: %p\n  Data: %p\n  Size: 0x%lx\n  Free: 0x%x\n  Next: %p\n",
            i++,
            chunk,
            chunk+1,
            chunk->size,
            chunk->free,
            chunk->next
        );
    }
}


void* malloc(size_t size)
{
    size_t allocsize = size + infoSize;

    void* currbrk = sbrk(0);

    if (HEAD == 0)
    {
        if (sbrk(allocsize) == (void*)-1)
        {
            return NULL;
        }

        HEAD = currbrk;
        HEAD->size = size;
        HEAD->free = 0;
        HEAD->next = NULL;

        return HEAD + 1;
    }

    chunkinfo* lastvalid = NULL;
    chunkinfo* curr = HEAD;
    chunkinfo* bestfit = NULL;
    while (curr != NULL)
    {
        // Try to find the best fitting free chunk
        if (curr->free && curr->size >= size)
        {
            if (curr->size == size)
            {
                bestfit = curr;
                break;
            }
            else
            {
                if (bestfit == NULL)
                {
                    bestfit = curr;
                    continue;
                }

                size_t diff = curr->size - size;
                size_t bestdiff = bestfit->size - size;
                if (diff < bestdiff)
                {
                    bestfit = curr;
                }
            }
        }
        lastvalid = curr;
        curr = curr->next;
    }

    // Use the best fit
    if (bestfit != NULL)
    {
        curr = bestfit;
    }

    if (curr != NULL)
    {
        // Found a free chunk that's large enough
        // We check size here instead of allocsize
        // we check the wrong size here, how do we exploit this
        if (curr->size > size*2)
        {
            chunkinfo* newchunk = ((void*)(curr+1)) + size;
            newchunk->free = 1;
            newchunk->next = curr->next;
            newchunk->size = curr->size - allocsize;
            curr->size = size;

            curr->next = newchunk;
        }

        curr->free = 0;
        return curr + 1;
    }
    else
    {
        if (lastvalid->free)
        {
            // Extend last chunk if free
            if (sbrk(allocsize - lastvalid->size) == (void*)-1)
            {
                return NULL;
            }
            lastvalid->size = size;
            lastvalid->free = 0;
            return lastvalid + 1;
        }
        else
        {
            // Add new chunk

            //check if there's any existing space we can use
            void* currdataend = (void*)(lastvalid+1) + lastvalid->size;
            size_t freespace = (size_t)currbrk - (size_t)currdataend;

            if (freespace < allocsize)
            {
                if (sbrk(allocsize - freespace) == (void*)-1)
                {
                    return NULL;
                }
            }

            chunkinfo* newchunk = currbrk;
            newchunk->size = size;
            newchunk->free = 0;
            newchunk->next = NULL;
            lastvalid->next = newchunk;
            return newchunk + 1;
        }
    }

    return NULL;
}


void free(void* ptr)
{
    void* freeme = ptr - sizeof(chunkinfo);

    chunkinfo* curr = HEAD;
    // Only free chunks we allocated
    while (curr != NULL)
    {
        // We don't check for double free
        if (curr == freeme)
        {
            curr->free = 1;
            chunkinfo* next = curr->next;

            // Combine with next chunk if free
            if (next != NULL && next->free)
            {
                curr->size += next->size + sizeof(chunkinfo);
                curr->next = next->next;
            }

            // We found the chunk to free so break
            break;
        }
        curr = curr->next;
    }

    // do a sweep to combine adjacent free chunks
    curr = HEAD;
    while (curr != NULL)
    {
        if (curr->free == 1 && curr->next != NULL && curr->next->free == 1)
        {
            chunkinfo* next = curr->next;
            curr->size += sizeof(chunkinfo) + next->size;
            curr->next = next->next;
        }
        curr = curr->next;
    }
}


void* realloc(void* ptr, size_t size)
{
    if (ptr == NULL)
        return malloc(size);

    if (size == 0)
    {
        free(ptr);
        return NULL;
    }

    void* targetchunk = ptr - sizeof(chunkinfo);

    chunkinfo* curr = HEAD;
    while (curr != NULL)
    {
        if (curr == targetchunk)
        {
            // If big enough do nothing
            if (curr->size >= size)
                return ptr;

            chunkinfo* next = curr->next;

            // Extend into next chunk if free
            if (next != NULL && next->free)
            {
                size_t newsize = curr->size + next->size + sizeof(chunkinfo);
                // Check if big enough if we take it over
                if (newsize < size)
                    break;
                curr->size = newsize;
                curr->next = next->next;
                // We could grow the chunk forward enough
                return curr+1;
            }
            break;
        }
        curr = curr->next;
    }

    // Alloc new chunk and copy existing data
    void* newchunk = malloc(size);
    if (curr != NULL)
    {
        memcpy(newchunk, curr+1, curr->size);
        free(curr+1);
    }
    return newchunk;
}
