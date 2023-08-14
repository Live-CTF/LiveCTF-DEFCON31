#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <sys/mman.h>

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void encode_uleb128(uint8_t* input, size_t count, uint8_t* output)
{
    uint8_t* outptr = output;
    uint8_t valueBits = 0;
    uint64_t value = 0;

    while (1)
    {
        while (valueBits > 7)
        {
            *outptr = 0x80 | (value & 0x7F);
            outptr++;
            value >>= 7;
            valueBits -= 7;
        }

        if (count == 0)
        {
            break;
        }

        count --;
        value |= (uint64_t)(input[count]) << valueBits;
        valueBits += 8;
    }
    *outptr = value;
    outptr++;
}

int main(int argc, char** argv, char** envp)
{
    init();
    printf("Give me some decoded shellcode:\n");

    char line[4096];
    size_t line_size = read(STDIN_FILENO, line, sizeof(char) * 4096);

    if (line_size > 0 && line[line_size - 1] == '\n')
    {
        line[line_size - 1] = 0;
        line_size --;
    }

    uint8_t encoded[4096];
    encode_uleb128((uint8_t*)line, line_size, encoded);

    void* ptr = mmap(NULL, sizeof(encoded), PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    memcpy(ptr, encoded, sizeof(encoded));
    ((void(*)())ptr)();

    return 0;
}
