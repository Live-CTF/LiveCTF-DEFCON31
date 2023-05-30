#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int main(int argc, char** argv) {
    int stars = atoi(argv[1]);
    // Find seed
    int seed = time(NULL) - 100;
    while (1) {
        seed += 1;
        srand(seed);
        // laby init: 590 rand()
        for (int i = 0; i < 590; i++) {
            rand();
        }
        // Check room stars
        int x = rand();
        if (((x >> 0xe) & 0xffffffff) == stars) {
            //fprintf(stderr, "%d\n", (x >> 0xe) & 0xffffffff);
            break;
        }
    }
    int total = 0;
    // 200 moves margin to move in the maze
    for (int i = 0; i < 200; i++) {
        int x = rand();
        //fprintf(stderr, "%d\n", (x >> 0xe) & 0xffffffff);
        total += 1;
    }
    // Waste moves to find the right rand
    while (1) {
        total += 1;
        int x = rand();
        if (x % 1213 == 1212) {
            break;
        }
    }
    printf("%d\n", total);
}
