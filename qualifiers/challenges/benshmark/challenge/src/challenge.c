#include <bits/time.h>
#define _GNU_SOURCE         /* See feature_test_macros(7) */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>

#include <linux/seccomp.h>  /* Definition of SECCOMP_* constants */
#include <sys/syscall.h>    /* Definition of SYS_* constants */
#include <unistd.h>
#include <sys/mman.h>
#include <seccomp.h>

#include <sys/prctl.h>

#define PROGRAM_TIMEOUT 60
#define JOB_TIMEOUT 1
#define MAX_RUNNING 5
#define MAX_FILE_NAME_LEN 64
#define CODE_SIZE 256

// Uncomment this to make the challenge easier
//#define RETCODE_SIDECHANNEL


struct run_result {
    int pid;
    int done;
    int returncode;
    char file[MAX_FILE_NAME_LEN];
    uint64_t start_time;
    uint64_t end_time;
    struct run_result* next;
};


struct run_result* HEAD_RESULT = NULL;
struct run_result* LAST_RESULT = NULL;


struct run_result* create_shared_run_result()
{
    int protection = PROT_READ | PROT_WRITE;
    int visibility = MAP_SHARED | MAP_ANONYMOUS;
    struct run_result* res = mmap(NULL, sizeof(struct run_result), protection, visibility, -1, 0);
    memset(res, 0, sizeof(struct run_result));
    return res;
}


void init_seccomp()
{
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_STRICT, 0, NULL))
    {
        exit(123);
    }
}


void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    signal(SIGALRM, exit);
    srand(time(NULL));
}


int count_running_tasks()
{
    int running = 0;
    struct run_result* res = HEAD_RESULT;
    while (res != NULL)
    {
        if (!res->done)
        {
            int pid;
            int status;
            pid = waitpid(res->pid, &status, WNOHANG);
            if (pid == 0)
                running += 1;
            else if (pid == -1)
            {
                printf("waitpid %s failed with errno %d\n", res->file, errno);
            }
            else
            {
                res->returncode = status;
                res->done = 1;
            }
        }
        res = res->next;
    }
    return running;
}


uint64_t gettime()
{
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC_RAW, &now);
    return (now.tv_sec * 1000) + (now.tv_nsec / 1000000);
}


void menu()
{
    puts("1. Run file");
    puts("2. Results");
    puts("3. Exit");
}


void run_file(const char* filename)
{
    // run with /proc/self/fd/0 or /dev/stdin to read in shellcode

    int f = open(filename, O_RDONLY);
    if (f == -1)
    {
        puts("Failed opening file");
        return;
    }

    struct run_result* result = create_shared_run_result();

    while (count_running_tasks() >= MAX_RUNNING)
    {
        puts("Max tasks running, waiting for an open slot...");
        sleep(1);
    }

    void* code = aligned_alloc(4096, 4096);
    if (code == NULL)
    {
        puts("malloc failed");
        return;
    }

    uint64_t read_bytes = read(f, code, CODE_SIZE);
    if (read_bytes == -1)
    {
        // Can be hit by trying to read file twice
        // Not closing the fd here means we can access it later from forked children
        puts("read failed");
        free(code);
        return;
    }

    if (mprotect(code, CODE_SIZE, PROT_READ|PROT_EXEC) == -1)
    {
        printf("mprotect failed %d\n", errno);
        free(code);
        return;
    }

    // Putting this in the child would mean the exploit needs to busy loop to avoid getting clobbered
    memcpy(result->file, filename, MAX_FILE_NAME_LEN);

    int orig_proc_id = getpid();
    int pid = fork();
    if (pid == 0)
    {
        // try and prevent zombies
        int r = prctl(PR_SET_PDEATHSIG, SIGTERM);
        if (r == -1) { perror(0); exit(1); }
        // test in case the original parent exited just
        // before the prctl() call
        if (getppid() != orig_proc_id)
            exit(1);

        alarm(JOB_TIMEOUT);
        fclose(stdin);
        fclose(stdout);
        result->start_time = gettime();
        init_seccomp();
        (*(void(*)()) code)();
        result->end_time = result->start_time + (random() % 1000);
        exit(1);
    }
    else
    {
        close(f);
        free(code);
        result->pid = pid;

        if (HEAD_RESULT == NULL)
            HEAD_RESULT = result;

        if (LAST_RESULT)
            LAST_RESULT->next = result;
        LAST_RESULT = result;
    }
}


void check_results()
{
    count_running_tasks();
    struct run_result* res = HEAD_RESULT;
    int i = 0;
    puts("Results:");
    while (res != NULL)
    {
        if (res->done)
        {
            if (res->end_time == 0)
            {
                #ifdef RETCODE_SIDECHANNEL
                printf("%s: Failed to complete, status: %d\n", res->file, res->returncode);
                #else
                printf("%s: Failed to complete\n", res->file);
                #endif
            }
            else
            {
                printf("%s: Took %lums\n", res->file, res->end_time - res->start_time);
            }
        }
        else
        {
            printf("%s: Started %lu\n", res->file, res->start_time);
        }
        res = res->next;
        i++;
    }
}


int main(int argc, char** argv, char** envp)
{
    init();

    alarm(PROGRAM_TIMEOUT);

    while (1)
    {
        menu();

        int choice;
        printf("Choice: ");
        if (scanf("%d", &choice) == EOF)
            return 0;

        switch (choice)
        {
        case 1:
        {
            char filename[MAX_FILE_NAME_LEN] = {0};
            printf("> ");
            if (!scanf("%63s", filename))
                break;
            run_file(filename);
            break;
        }
        case 2:
            check_results();
            break;
        case 3:
            return 0;
        default:
            puts("Invalid choice");
            break;
        }
    }

    return 0;
}
