#include "alloc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// padding for older gcc
char myVar[8] __attribute__ ((section (".got"))) = { 0 };

typedef struct {
    uint32_t size;
    char* name;
} Furniture;

typedef struct {
    char* name;
    size_t size;
    size_t item_count;
    Furniture** furniture_items;
} Room;

typedef struct {
    char* name;
    size_t room_count;
    Room** rooms;
} House;


House house = {0};
char* NAME = NULL;



void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

size_t read_string(char* buf, size_t maxlen)
{
    char c;
    size_t len = 0;
    while ((c = fgetc(stdin)) != EOF && len < (maxlen - 1))
    {
        if (c == '\n')
            break;
        buf[len] = c;
        len++;
    }
    buf[len] = '\0';
    return len;
}

void describe_house()
{
    if (NAME != NULL)
    {
        printf("%s's ", NAME);
    }
    printf("House: %s\n", house.name);
    for (size_t i = 0; i < house.room_count; i++)
    {
        Room* room = house.rooms[i];
        printf("  Room: %s (%lu sqft)\n", room->name, room->size);
        for (size_t j = 0; j < room->item_count; j++)
        {
            Furniture* item = room->furniture_items[j];
            printf("    Item: %s (%u sqft)\n", item->name, item->size);
        }
    }
}

void add_room()
{
    char room_name[32] = {0};
    printf("Room name: ");
    if (scanf("%31s", room_name) == EOF)
        return;

    uint64_t room_size;
    printf("Room size: ");
    if (scanf("%lu", &room_size) == EOF)
        return;

    Room* room = malloc(sizeof(Room));
    room->name = malloc(32);
    strcpy(room->name, room_name);

    room->size = room_size;
    room->item_count = 0;
    room->furniture_items = NULL;

    house.rooms = realloc(house.rooms, sizeof(Room*)*(house.room_count + 1));
    house.rooms[house.room_count] = room;
    house.room_count++;

    describe_house();
}

Room* get_room_by_name(char* name)
{
    for (size_t i = 0; i < house.room_count; i++)
    {
        if (strcmp(house.rooms[i]->name, name) == 0)
        {
            return house.rooms[i];
        }
    }
    return NULL;
}

Furniture* get_item_by_name(Room* room, char* name)
{
    for (size_t i = 0; i < room->item_count; i++)
    {
        Furniture* item = room->furniture_items[i];
        if (strcmp(item->name, name) == 0)
        {
            return item;
        }
    }
    return NULL;
}

void add_furniture()
{
    char room_name[32] = {0};
    printf("Room name: ");
    if (scanf("%31s", room_name) == EOF)
        return;
    Room* room = get_room_by_name(room_name);

    if (room == NULL)
    {
        puts("Could not find room");
        return;
    }

    char item_name[32] = {0};
    printf("Item name: ");
    if (scanf("%31s", item_name) == EOF)
        return;
    uint32_t item_size;
    printf("Item size: ");
    if (scanf("%u", &item_size) == EOF)
        return;

    // make sure we wouldn't overfill the room

    size_t remaining_sqft = room->size;
    for (size_t i = 0; i < room->item_count; i++)
    {
        remaining_sqft -= room->furniture_items[i]->size;
    }

    if (item_size > remaining_sqft)
    {
        printf("Item is too big! There's only %lusqft left!\n", remaining_sqft);
        return;
    }

    Furniture* item = malloc(sizeof(Furniture));
    item->name = malloc(32);
    strcpy(item->name, item_name);
    item->size = item_size;

    room->furniture_items = realloc(room->furniture_items, sizeof(Furniture*)*(room->item_count + 1));
    room->furniture_items[room->item_count] = item;
    room->item_count++;
    describe_house();
}


void remove_room()
{
    char room_name[32] = {0};
    printf("Room name: ");
    if (scanf("%31s", room_name) == EOF)
        return;

    Room* room = get_room_by_name(room_name);

    if (room == NULL)
        return;

    // shift room array
    size_t room_idx = 0;
    for (size_t i = 0; i < house.room_count; i++)
    {
        if (house.rooms[i] == room)
        {
            room_idx = i;
            break;
        }
    }

    for (size_t i = room_idx; i < house.room_count-1; i++)
    {
        house.rooms[i] = house.rooms[i+1];
    }

    // free furniture
    for (size_t i = 0; i < room->item_count; i++)
    {
        Furniture* item = room->furniture_items[i];
        free(item->name);
        free(item);
    }
    free(room->furniture_items);

    // free room+name
    free(room->name);
    free(room);

    house.room_count--;

    house.rooms = realloc(house.rooms, sizeof(Room*)*house.room_count);

    describe_house();
}


void remove_furniture()
{
    char buf[32] = {0};
    printf("Room name: ");
    if (scanf("%31s", buf) == EOF)
        return;

    Room* room = get_room_by_name(buf);

    if (room == NULL)
        return;

    printf("Item name: ");
    if (scanf("%31s", buf) == EOF)
        return;


    Furniture* item = get_item_by_name(room, buf);

    if (item == NULL)
        return;

    // shift items array
    size_t item_idx = 0;
    for (size_t i = 0; i < room->item_count; i++)
    {
        if (room->furniture_items[i] == item)
        {
            item_idx = i;
            break;
        }
    }

    for (size_t i = item_idx; i < room->item_count-1; i++)
    {
        room->furniture_items[i] = room->furniture_items[i+1];
    }

    // free item and name
    free(item->name);
    free(item);
    room->item_count--;

    room->furniture_items = realloc(room->furniture_items, sizeof(Furniture*)*room->item_count);

    describe_house();
}


void rename_house()
{
    char buf[128] = {0};
    printf("House name: ");
    size_t numread = read_string(buf, 128);
    if (numread == 0)
        return;
    house.name = realloc(house.name, numread+1);
    memcpy(house.name, buf, numread+1);
}


void change_name()
{
    char buf[128] = {0};
    printf("Name: ");
    size_t numread = read_string(buf, 128);
    if (numread == 0)
        return;
    NAME = realloc(NAME, numread+1);
    memcpy(NAME, buf, numread+1);
}


int main(int argc, char** argv, char** envp)
{
    init();

    rename_house();

    while (1)
    {
        puts("1. Add new room\n"
        "2. Remove room\n"
        "3. Add furniture to room\n"
        "4. Remove furniture from room\n"
        "5. Show house\n"
        "6. Rename house\n"
        "7. Change name\n"
        "8. Exit");
        int choice;
        printf("Choice: ");
        if (scanf("%d", &choice) == EOF)
            return 0;

        switch (choice)
        {
            case 1:
                add_room();
                break;
            case 2:
                remove_room();
                break;
            case 3:
                add_furniture();
                break;
            case 4:
                remove_furniture();
                break;
            case 5:
                //if (strcmp(house.name, "DEBUG") == 0)
                    print_state();
                describe_house();
                break;
            case 6:
                rename_house();
                break;
            case 7:
                change_name();
                break;
            case 8:
                exit(0);
            default:
                puts("Invalid choice");
                break;
        }
    }

    return 0;
}

void win(void)
{
    char *argv[]={"/bin/sh", NULL};
    int ret;
    __asm__ volatile ("syscall"
    :"=a" (ret)
    :"a"(59), // syscall number (execve)
    "D"(argv[0]), // filename
    "S"(argv), // arguments
    "d"(0) // env
    :"rcx","r11","cc");
}
