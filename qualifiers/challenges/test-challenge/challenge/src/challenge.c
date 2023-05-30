#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void win(void)
{
    system("/bin/sh");
}

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int main(int argc, char** argv, char** envp)
{
    init();

    char buf[32] = { 0 };
    puts("Give me input: ");
    fgets(buf, 1024, stdin);
    printf("You sent: %s\n", buf);
    if(strncmp("WIN", buf, 3) == 0) {
        win();
    }

    return 0;
}
