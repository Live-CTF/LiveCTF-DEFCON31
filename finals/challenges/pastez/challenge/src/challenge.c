#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <time.h>
#include <stdbool.h>

#define MSG_LEN 256

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

// I don't believe this to be solvable without these unfortunately.
// Binary is too small to have these "naturally", and leaking libc as part of the chal
// makes it a bit too easy IMO.
__attribute__((naked)) void useful_things() {
     __asm__(
             "pop %rdi; ret;"
             "pop %rsi; ret;"
             "pop %rdx; ret;"
             "pop %rcx; ret;"
    );
}

const char* bad_words[] = {
    "hack",
    "hacking",
};

struct Message {
    time_t time;
    char content[MSG_LEN];
    struct Message* next;
};

struct Message* message_head = NULL;

__attribute__ ((noinline)) void sanitize(char *dst, char *src) {
    char buffer[MSG_LEN] = {0};
    char *cur_in = src;
    char *cur_out = buffer;
    char *word_end;
    while (cur_in < src + MSG_LEN && (word_end = strchr(cur_in, ' ')) != NULL) {
        *word_end = 0;
        bool replaced = false;
        for (int i = 0; i < sizeof(bad_words)/sizeof(bad_words[0]); i++) {
            if (!strcasecmp(cur_in, bad_words[i])) {
                cur_out = stpcpy(cur_out, "[deleted]");
                replaced = true;
                break;
            }
        }
        if (!replaced) {
            cur_out = stpcpy(cur_out, cur_in);
        }
        cur_out = stpcpy(cur_out, " ");
        cur_in += (word_end - cur_in) + 1;
    }
    if (cur_in != src + MSG_LEN) {
        memcpy(cur_out, cur_in, src + MSG_LEN - cur_in);
    }
    memcpy(dst, buffer, MSG_LEN);
}

void insert_message(time_t time, char *content) {
    struct Message* new_message = (struct Message*)malloc(sizeof(struct Message));
    new_message->time = time;
    sanitize(new_message->content, content);

    new_message->next = message_head;
    message_head = new_message;
}

void edit_message(struct Message* message) {
    char buffer[MSG_LEN] = {0};
    printf("Enter the new message: ");
    read(STDIN_FILENO, buffer, sizeof(buffer));
    sanitize(message->content, buffer);
    puts("Message edited successfully.");
}

void delete_message(struct Message* message) {
    if (message == message_head) {
        message_head = message->next;
    } else {
        struct Message* current = message_head;
        while (current != NULL && current->next != message) {
            current = current->next;
        }
        if (current != NULL) {
            current->next = message->next;
        }
    }
    free(message);
}

void print_messages() {
    struct Message* current = message_head;
    int id = 1;

    while (current != NULL) {
        printf("%d - @%ld: %s\n", id, current->time, current->content);

        current = current->next;
        id++;
    }
}

void rud_messages() {
    print_messages();

    int selected_id;
    printf("Enter the ID of the message you want to view/edit/delete (0 to cancel): ");
    scanf("%d", &selected_id);

    if (selected_id == 0) {
        return;
    }

    selected_id--;

    int i;
    struct Message *selected_message = message_head;
    for (i = 0; selected_message != NULL && i < selected_id; selected_message = selected_message->next, i++) { };
    
    if (i != selected_id || selected_message == NULL) {
        puts("Invalid ID");
        return;
    }

    puts("Selected Message:");
    printf("%ld: %s\n", selected_message->time, selected_message->content);

    int choice;
    printf("1. Edit Message\n2. Delete Message\nEnter your choice: ");
    scanf("%d", &choice);

    if (choice == 1) {
        edit_message(selected_message);
    } else if (choice == 2) {
        delete_message(selected_message);
        puts("Message deleted successfully.");
    }
}

int main() {
    init();

    while (1) {
        printf("1. View/Edit Messages\n2. Create Message\n3. Exit\nEnter your choice: ");

        int choice;
        scanf("%d", &choice);

        if (choice == 1) {
            rud_messages();
        } else if (choice == 2) {
            char buffer[MSG_LEN] = {0};
            time_t raw_time;

            time(&raw_time);

            printf("Enter your message: ");
            read(STDIN_FILENO, buffer, sizeof(buffer));

            insert_message(raw_time, buffer);
            puts("Message saved successfully.");
        } else if (choice == 3) {
            return 0;
        } else {
            puts("Invalid choice. Try again.");
        }
    }
}
