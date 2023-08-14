#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

// This binary is too small to have good gadgets, and this _really_ isn't supposed to be
// an exercise in stupid rop chains with no good gadgets...
__attribute__((naked)) void all_the_gadgets()
{
    __asm__(
        "pop %rax\nret\n"
        "pop %rbx\nret\n"
        "pop %rcx\nret\n"
        "pop %rdx\nret\n"
        "pop %rsi\nret\n"
        "pop %rdi\nret\n"
        "pop %rsp\nret\n"
        "pop %rbp\nret\n"
        "pop %r8\nret\n"
        "pop %r9\nret\n"
        "pop %r10\nret\n"
        "pop %r11\nret\n"
        "pop %r12\nret\n"
        "pop %r13\nret\n"
        "pop %r14\nret\n"
        "pop %r15\nret\n"
        "mov %rax, %rax\nret\n"
        "mov %rax, %rbx\nret\n"
        "mov %rax, %rcx\nret\n"
        "mov %rax, %rdx\nret\n"
        "mov %rax, %rsi\nret\n"
        "mov %rax, %rdi\nret\n"
        "mov %rax, %rsp\nret\n"
        "mov %rax, %rbp\nret\n"
        "mov %rax, %r8\nret\n"
        "mov %rax, %r9\nret\n"
        "mov %rax, %r10\nret\n"
        "mov %rax, %r11\nret\n"
        "mov %rax, %r12\nret\n"
        "mov %rax, %r13\nret\n"
        "mov %rax, %r14\nret\n"
        "mov %rax, %r15\nret\n"
        "mov %rax, %rax\nret\n"
        "mov %rbx, %rax\nret\n"
        "mov %rcx, %rax\nret\n"
        "mov %rdx, %rax\nret\n"
        "mov %rsi, %rax\nret\n"
        "mov %rdi, %rax\nret\n"
        "mov %rsp, %rax\nret\n"
        "mov %rbp, %rax\nret\n"
        "mov %r8, %rax\nret\n"
        "mov %r9, %rax\nret\n"
        "mov %r10, %rax\nret\n"
        "mov %r11, %rax\nret\n"
        "mov %r12, %rax\nret\n"
        "mov %r13, %rax\nret\n"
        "mov %r14, %rax\nret\n"
        "mov %r15, %rax\nret\n"
        "mov 0(%rax), %rcx\nret\n"
        "mov %rcx, 0(%rax)\nret\n"
        "syscall\nret\n"
    );
}

uint64_t read_int(const char* message)
{
    uint64_t result;
    printf("%s\n", message);
    scanf("%" SCNx64, &result);
    return result;
}

int main(int argc, char** argv, char** envp)
{
    init();

    // Leak a bunch of stuff we will need
    // Not leaking libc because onegadget also because I'm too lazy to look up how
    int pty = posix_openpt(O_RDWR | O_NOCTTY);
    printf("posix_openpt() returned 0x%x\n", pty);
    printf("main is %p and argc is %p\n", &main, &argc);

    while (1) {
        uint64_t fd = read_int("What fd do you want?");
        uint64_t number = read_int("What ioctl do you want to call?");
        uint64_t nargs = read_int("How many arguments do you want?");

        uint64_t arg1;
        uint64_t arg2;
        uint64_t arg3;
        uint64_t arg4;

        // iirc ioctl only takes one argument, but this challenge would not be very
        // doable if you didn't have scratch space to read from
        if (nargs > 4) {
            printf("Too many arguments! Try <= 4!\n");
            continue;
        }

        int result = 0;

        errno = 0;
        switch (nargs) {
        case 0:
            result = ioctl(fd, number);
            break;
        case 1:
            arg1 = read_int("What do you want for arg1?");
            result = ioctl(fd, number, arg1);
            break;
        case 2:
            arg1 = read_int("What do you want for arg1?");
            arg2 = read_int("What do you want for arg2?");
            result = ioctl(fd, number, arg1, arg2);
            break;
        case 3:
            arg1 = read_int("What do you want for arg1?");
            arg2 = read_int("What do you want for arg2?");
            arg3 = read_int("What do you want for arg3?");
            result = ioctl(fd, number, arg1, arg2, arg3);
            break;
        case 4:
            arg1 = read_int("What do you want for arg1?");
            arg2 = read_int("What do you want for arg2?");
            arg3 = read_int("What do you want for arg3?");
            arg4 = read_int("What do you want for arg4?");
            result = ioctl(fd, number, arg1, arg2, arg3, arg4);
            break;
        }

        printf("ioctl returned 0x%x\n", result);
        if (errno != 0) {
            perror("ioctl error");
        }

        if (read_int("Do another (0/1)?") == 0) {
            break;
        }
    }

    return 0;
}
