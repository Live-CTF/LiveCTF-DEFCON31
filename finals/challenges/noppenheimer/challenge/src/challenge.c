#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <stdint.h>
#include <string.h>

#define CODE_SIZE 0x1000
#define BOARD_COLS 16
#define BOARD_ROWS CODE_SIZE / BOARD_COLS

char* CODE_ARENA = NULL;

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void print_board()
{
    puts("BOARD:");
    for (size_t y = 0; y < BOARD_ROWS; y++)
    {
        for (size_t x = 0; x < BOARD_COLS; x++)
        {
            printf("%02hhx ", CODE_ARENA[(y*BOARD_COLS) + x]);
        }
        puts("");
    }
}

void nuke(uint32_t originx, uint32_t originy)
{
    for (int dy = -1; dy <= 1; dy++)
    {
        for (int dx = -1; dx <= 1; dx++)
        {
            if (dy != 0 && dx != 0)
                continue;

            int x = originx + dx;
            int y = originy + dy;

            if (x < 0 || y < 0 || x >= BOARD_COLS || y >= BOARD_ROWS)
                continue;
            CODE_ARENA[(y*BOARD_COLS) + x] = '\x90';
        }
    }
}

int main(int argc, char** argv, char** envp)
{
    init();

    srand(1945716);

    CODE_ARENA = aligned_alloc(0x1000, CODE_SIZE);

    for (size_t i = 0; i < CODE_SIZE; i++)
    {
        CODE_ARENA[i] = rand() % 256;
    }

    if (mprotect(CODE_ARENA, CODE_SIZE, PROT_READ|PROT_WRITE|PROT_EXEC) == -1)
    {
        puts("Failed to mprotect page");
        exit(1);
    }

    char buf[32] = {0};
    while (1)
    {
        puts("Options:\n"
        "LAUNCH x,y - Launch a test at position x,y\n"
        "VIEW - See state of test site\n"
        "ENDTEST - Conclude testing");
        printf("> ");
        if (fgets(buf, 32, stdin) == NULL)
            return 0;

        buf[strcspn(buf, "\n")] = 0;

        if (strcmp(buf, "ENDTEST") == 0)
            break;

        if (strcmp(buf, "VIEW") == 0)
        {
            print_board();
            continue;
        }

        if (strncmp(buf, "LAUNCH ", 7) == 0)
        {
            uint32_t x = 0;
            uint32_t y = 0;
            if (sscanf(buf+7, "%u,%u", &x, &y) == EOF)
            {
                exit(0);
            }
            nuke(x, y);
            continue;
        }
    }

    (*(void(*)()) CODE_ARENA)();

    return 0;
}
