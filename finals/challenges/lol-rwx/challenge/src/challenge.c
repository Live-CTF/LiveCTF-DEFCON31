#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <sys/mman.h>
#include <unistd.h>

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int main(int argc, char** argv, char** envp)
{
    init();
    mprotect(0x401000, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);

    printf("SUDDEN DEATH !! .TEXT IS RWX !!\n");

    while (1)
    {
        printf("Where to write? (hex)\n");
        char input[0x20];
        uint64_t addr;
        fscanf(stdin, "%lx", &addr);

        printf("What to write? (hex)\n");
        uint64_t data;
        fscanf(stdin, "%lx", &data);

        *((uint64_t*)addr) = data;

        printf("Do another?\n");
        uint64_t another;
        fscanf(stdin, "%d", &another);

        if (!another)
        {
            break;
        }
    }

    printf("What is the chance execution actually gets this far?\n");
    return 0;
}
