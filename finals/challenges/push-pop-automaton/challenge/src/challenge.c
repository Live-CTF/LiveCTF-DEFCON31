#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

enum vm_opcode_t
{
    Push = 'u', // scanf %hhx sp, sp -= 2
    Pop  = 'o', // printf %hhx *sp, sp += 2
    Halt = 'h', // return
};

struct vm_state_t
{
    uint8_t memory[0x1000];
    int16_t pc; // 1000
    int16_t sp; // 1002
};

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void win(void)
{
    system("/bin/sh");
}

void interpreter(struct vm_state_t* vm)
{
    while (1)
    {
        switch (vm->memory[vm->pc])
        {
            case Push:
                vm->memory[--vm->sp] = getchar();
                vm->memory[--vm->sp] = getchar();
                break;
            case Pop:
                putchar(vm->memory[vm->sp++]);
                putchar(vm->memory[vm->sp++]);
                break;
            case Halt:
                return;
        }
        vm->pc ++;
    }
}

int main(int argc, char** argv, char** envp)
{
    init();

    struct vm_state_t vm;
    memset((void*)&vm, 0, sizeof(struct vm_state_t));

    int i;
    for (i = 0; i < sizeof(vm.memory); i ++) {
        int ch = getchar();
        if (ch == 'u')
            vm.memory[i] = Push;
        if (ch == 'o')
            vm.memory[i] = Pop;
        if (ch == 'h')
            vm.memory[i] = Halt;
        if (ch == '\n')
            break;
    }

    vm.pc = 0;
    vm.sp = i;

    interpreter(&vm);

    return 0;
}
