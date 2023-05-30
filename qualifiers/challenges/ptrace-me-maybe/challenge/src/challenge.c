#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
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

    pid_t child_pid = fork();
    if (child_pid == 0) {
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        kill(getpid(), SIGSTOP);
        return 0;
    }

    int status;
    ptrace(PTRACE_ATTACH, child_pid, NULL, NULL);
    do {
        waitpid(child_pid, &status, 0);
    } while (!WIFSTOPPED(status));

    while (1) {
        uint64_t request = read_int("What ptrace request do you want to send?");
        uint64_t addr = read_int("What address do you want?");
        uint64_t data = read_int("What do you want copied into data?");

        errno = 0;
        long result = ptrace(request, child_pid, addr, data);

        printf("ptrace returned 0x%lx\n", result);
        if (errno != 0) {
            perror("ptrace error");
        }

        if (read_int("Do another (0/1)?") == 0) {
            break;
        }
    }

    ptrace(PTRACE_DETACH, child_pid, NULL, NULL);
    waitpid(child_pid, &status, 0);

    return 0;
}
