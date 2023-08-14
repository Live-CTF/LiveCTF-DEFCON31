#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "rc4.h"
#include "flag.h"

#define NO_PATH UINT64_MAX

uint64_t *get_edge(size_t i, size_t j, uint64_t *w, size_t N)
{
    return &w[j * N + i];
}

uint64_t mystery_algorithm(size_t i, size_t j, size_t k, uint64_t *w, size_t N)
{
    if (k == -1)
    {
        uint64_t res = *get_edge(i, j, w, N);
        return res;
    }

    uint64_t alt1 = mystery_algorithm(i, j, k - 1, w, N);

    uint64_t alt2a = mystery_algorithm(i, k, k - 1, w, N);
    uint64_t alt2b = mystery_algorithm(k, j, k - 1, w, N);
    uint64_t alt2;

    if (alt2a == NO_PATH || alt2b == NO_PATH || (alt2a >= 0 && (INT64_MAX - alt2a) < alt2b))
    {
        alt2 = NO_PATH;
    }
    else
    {
        alt2 = alt2a + alt2b;
    }

    if (alt1 == NO_PATH && alt2 == NO_PATH)
    {
        return NO_PATH;
    }

    if (alt1 == NO_PATH)
    {
        return alt2;
    }

    if (alt1 < alt2)
    {
        return alt1;
    }
    else
    {
        return alt2;
    }
}

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void init_state(uint64_t *d, size_t N)
{
    for (size_t i = 0; i < N; i++)
    {
        for (size_t j = 0; j < N; j++)
        {
            *get_edge(i, j, d, N) = NO_PATH;
        }
    }
}

void decrypt_flag_with_solution(uint64_t *d, size_t dsize)
{
    char flag[FLAG_LEN];
    RC4((unsigned char *)d, dsize, flag_encrypted, (unsigned char *)flag, FLAG_LEN);
    printf("Flag: %s\n", flag);
}

int main(int argc, char **argv, char **envp)
{
    init();

    size_t N = PROBLEM_SIZE;
    size_t dsize = sizeof(uint64_t) * N * N;

    // Calculate the shortest path from i to j for all (i, j) pairs
    uint64_t *d = malloc(dsize);
    init_state(d, N);

    for (size_t i = 0; i < N; i++)
    {
        for (size_t j = 0; j < N; j++)
        {
            uint64_t path = mystery_algorithm(i, j, N - 1, w, N);
            *get_edge(i, j, d, N) = path;
        }
    }

    decrypt_flag_with_solution(d, dsize);
    free(d);

    return 0;
}
