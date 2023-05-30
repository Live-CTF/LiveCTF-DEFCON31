#include <stdint.h>
#include <sys/mman.h>
#include <sys/syscall.h>


uint64_t syscall(
    uint64_t number,
    uint64_t arg1,
    uint64_t arg2,
    uint64_t arg3,
    uint64_t arg4,
    uint64_t arg5
);

// seed, a, c
// Turbo Pascal LCG values because why not
static uint32_t RAND_STATE[4] = {1, 134775813, 1};

static int RAND_VAL = 0;

extern void (*__init_array_start []) (void) __attribute__((weak));
extern void (*__init_array_end []) (void) __attribute__((weak));

extern void (*__executable_start []) (void) __attribute__((weak));

extern void (*__fini_array_end []) (void) __attribute__((weak));
extern void (*__data_start []) (void) __attribute__((weak));


extern char __start_encrypted[];
extern char __stop_encrypted[];


uint32_t next_rand()
{
    // implicit mod 2**32
    RAND_STATE[0] = (RAND_STATE[1] * RAND_STATE[0]) + RAND_STATE[2];
    return RAND_STATE[0];
}


int inline_write(const char* buf, uint64_t count)
{
    return syscall(SYS_write, 1, (uint64_t)buf, count, 0, 0);
}


int inline_puts(const char* s)
{
    unsigned int count = 0;
    while (*(s + count) != '\0')
    {
        count++;
    }
    return inline_write(s, count);
}


static void inline_exit(int status)
{
    syscall(SYS_exit, status, 0, 0, 0, 0);
}


uint64_t get_random(void* buf, uint64_t buflen)
{
    return syscall(SYS_getrandom, (uint64_t)buf, buflen, 0, 0, 0);
}


void inline_readline(char* buf, size_t nbyte)
{
    int numread = syscall(SYS_read, 0, (uint64_t)buf, nbyte, 0, 0);
    if (numread <= 0)
        inline_exit(1);
}


int __attribute__((always_inline)) inline_mprotect(void* addr, uint64_t len, int flags)
{
    return (int) syscall(SYS_mprotect, (uint64_t)addr, len, flags, 0, 0);
}


int read_int()
{
    char buf[4] = {0};
    inline_readline(buf, sizeof(buf));
    return *((int*)buf);
}


uint64_t read_long()
{
    char buf[8] = {0};
    inline_readline(buf, sizeof(buf));
    return *((uint64_t*)buf);
}


void __attribute__((noinline, section("encrypted"), __aligned__(0x1000))) real_main()
{
    // It's probably fine if they overwrite got entries here
    uint64_t addr = (uint64_t)__executable_start;
    inline_write(&addr, 8);
    while (1)
    {
        addr = read_long();

        // Do not allow writing to the got
        if ((addr >= (uint64_t)__fini_array_end && addr <= (uint64_t)__data_start))
        {
            inline_exit(4);
        }

        if (addr == 0)
            break;

        *((uint64_t*)addr) = read_long();
    }
    return;
}


void __attribute__((constructor)) init_rand_val()
{
    // This can be skipped by getting arb write in first init entry
    if (get_random(&RAND_STATE, 4) == -1)
    {
        inline_puts("Random seed failed");
        inline_exit(1);
    }
    RAND_VAL = next_rand();
}


void early_mprotect()
{
    //uint64_t enc_base = (uint64_t)__start_encrypted - ((uint64_t)__start_encrypted % 4096);
    // If this isn't page aligned something's wrong
    uint64_t enc_base = (uint64_t)__start_encrypted;
    uint64_t enc_len = (uint64_t)__stop_encrypted - enc_base;
    if (inline_mprotect((void*)enc_base, enc_len, PROT_WRITE|PROT_READ|PROT_EXEC))
    {
        inline_exit(2);
    }
}


void late_mprotect()
{    uint64_t enc_base = (uint64_t)__start_encrypted - ((uint64_t)__start_encrypted % 4096);
    uint64_t enc_len = (uint64_t)__stop_encrypted - enc_base;
    if (inline_mprotect((void*)enc_base, enc_len, PROT_READ|PROT_EXEC))
    {
        inline_exit(2);
    }
}


void do_preinit()
{
    __init_array_start[0] = (void*)real_main;
    for (char* i = __start_encrypted; i < __stop_encrypted; i++)
    {
        *i = (*i) ^ 0x41;
    }
}


#pragma GCC push_options
#pragma GCC optimize ("O0")

__attribute__((section(".preinit_array"))) static void (*_[])(void) = { &early_mprotect, &do_preinit, &late_mprotect};

#pragma GCC pop_options


int main(int argc, char** argv, char** envp)
{
    for (int guess_num = 1; guess_num <= 256; guess_num++)
    {
        if (read_int() == RAND_VAL)
        {
            inline_puts("Correct!\n");
            return 0;
        }
        else
        {
            inline_puts("Incorrect\n");
        }
    }

    inline_puts("Failed!\n");
    inline_exit(1);
}

