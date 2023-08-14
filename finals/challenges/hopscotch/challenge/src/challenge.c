#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
#include <setjmp.h>
#include <locale.h>
#ifdef __APPLE__
#include <libc.h>
#endif

void debugString(char* input)
{
    char* _ = malloc(1048);
    snprintf(_, 1048, input);
    return;
}

void REMAP_PAGE_AS_READ_AND_EXECUTABLE(void * code)
{
    int pagesize = 0x1000;
    if (mprotect((void *)((uintptr_t)code & ~(pagesize - 1)), pagesize, PROT_READ | PROT_EXEC) == -1) {
        perror("mprotect");
        return;
    }
}
void REMAP_PAGE_AS_READ_AND_WRITE(void * code)
{
    int pagesize = 0x1000;
    if (mprotect((void *)((uintptr_t)code & ~(pagesize - 1)), pagesize, PROT_READ | PROT_WRITE) == -1) {
        perror("mprotect");
        return;
    }
}

void veryPoorlyWrittenWeirdStringPrinter(char* addr) {
    typedef void (*func_t)(void);

    char* outputString = malloc(0x1000);
    memset(outputString, 0, 0x1000);
    size_t inputPos = 0;
    size_t outputPos = 0;
    for (size_t i = 0; i < 0x1000; i++)
    {
        if (inputPos && (inputPos % 4) == 0)
            inputPos += 4;
        outputString[outputPos] = addr[inputPos];
        inputPos++;
        outputPos++;
    }
    outputString[0x1000-1] = 0;
    puts("the AWESOME string:");
    printf("%s\n", outputString);

    debugString("Now, We have to check if we're trying to be hacked by seeing if this string is ACTUALLY valid code");
    debugString("ChatGPT said this was a good, foolproof idea.");
    void *code = addr;
    REMAP_PAGE_AS_READ_AND_EXECUTABLE(code);

    ((func_t)code)();

    REMAP_PAGE_AS_READ_AND_WRITE(code);
}

void* convertToWeirdString(char* input)
{
    debugString("chatGPT says we should split our strings every 4 bytes because its more secure.");
    debugString("it also says we should pad them out with \'\\x40\' as well. I trust chatGPT.");

    char* inputString = malloc(0x1000);
    memset(inputString, '\x40', 0x1000);
    size_t inputPos = 0;
    size_t outputPos = 0;
    for (size_t i = 0; i < 0x1000; i++)
    {
        if (outputPos && (outputPos % 4) == 0)
            outputPos += 4;
        inputString[outputPos] = input[inputPos];
        if (input[inputPos] == 0)
            break;
        inputPos++;
        outputPos++;
    }
    return inputString;
}

void win()
{
    system("/bin/sh");
}

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}


int main() {
    init();

    printf("enter an AWESOME string:\n");
    char* inputString = malloc((0x1000/2)+1);
    fgets(inputString, (0x1000/2), stdin);
    void* writtenString = convertToWeirdString(inputString);

    veryPoorlyWrittenWeirdStringPrinter(writtenString);
}
