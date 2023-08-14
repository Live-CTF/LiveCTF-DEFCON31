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
    printf("SUDDEN DEATH !! HAVE YOU TRIED ?? TI GNISREVER\n");

    char response[0x101] = {0};
    fgets(response, 0x101, stdin);

    for (int64_t i = 0; i < 0x80; i ++)
    {
        char tmp = response[i];
        response[i] = response[0xff - i];
        response[0xff - i] = tmp;
    }

    bool success = true;
    success &= (response[30] == 'Y');
    success &= (response[29] == 'e');
    success &= (response[28] == 's');
    success &= (response[27] == ',');
    success &= (response[26] == ' ');
    success &= (response[25] == 'I');
    success &= (response[24] == ' ');
    success &= (response[23] == 'h');
    success &= (response[22] == 'a');
    success &= (response[21] == 'v');
    success &= (response[20] == 'e');
    success &= (response[19] == ' ');
    success &= (response[18] == 't');
    success &= (response[17] == 'r');
    success &= (response[16] == 'i');
    success &= (response[15] == 'e');
    success &= (response[14] == 'd');
    success &= (response[13] == ' ');
    success &= (response[12] == '.');
    success &= (response[11] == 't');
    success &= (response[10] == 'i');
    success &= (response[9] == ' ');
    success &= (response[8] == 'g');
    success &= (response[7] == 'n');
    success &= (response[6] == 'i');
    success &= (response[5] == 's');
    success &= (response[4] == 'r');
    success &= (response[3] == 'e');
    success &= (response[2] == 'v');
    success &= (response[1] == 'e');
    success &= (response[0] == 'r');

    if (!success) {
        printf("Hmm, seems like maybe you should.\n");
        return 1;
    }

    printf("Wow, clearly you have. Go get a shell: \n");

    mprotect(&response[0], sizeof(response), PROT_READ | PROT_WRITE | PROT_EXEC);
    ((void(*)())&response[31])();

    return 0;
}
