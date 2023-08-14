#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdint.h>


#define PROGRAM_TIMEOUT 300


struct Item {
    size_t id;
    size_t cost;
    const char* name;
    const char* desc;
};


struct Cart {
    size_t item_count;
    struct Item* items;
};


struct User {
    uint8_t admin;
    struct Cart* cart;
    char* username;
    char* password;
    struct User* nextUser;
};


typedef struct Cart Cart;
typedef struct Item Item;
typedef struct User User;


Item ITEMS[] = {
    { .id=0, .cost=2500, .name="Apple", .desc = "Apples have always been overpriced" },
    { .id=1, .cost=30, .name="Banana", .desc = "For measurement" },
    { .id=2, .cost=15, .name="Carrot", .desc = "It could help with bad eyesight" },
    { .id=3, .cost=100, .name="Durian", .desc = "More smelly than spiky" },
    { .id=4, .cost=10, .name="Egg", .desc = "egg." },
    { .id=5, .cost=31337, .name="Flag", .desc = "Big enough to share" },
};

const int NUM_ITEMS = sizeof(ITEMS) / sizeof(Item);

User* BASE_USER = NULL;
User* CURRENT_USER = NULL;


void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}


void add_item()
{
    uint32_t choice;
    printf("Item: ");
    if (scanf("%u", &choice) == EOF)
        return;

    if (choice >= NUM_ITEMS)
    {
        puts("Invalid item");
        return;
    }

    Item item = ITEMS[choice];

    Cart* cart = CURRENT_USER->cart;
    void* newMem = realloc(cart->items, sizeof(Item)*(cart->item_count+1));
    if (newMem == NULL)
    {
        puts("Error adding item");
        return;
    }
    cart->item_count += 1;
    cart->items = newMem;
    memcpy(&cart->items[cart->item_count - 1], &item, sizeof(Item));
}


void remove_item()
{
    uint32_t choice;
    printf("Item: ");
    if (scanf("%u", &choice) == EOF)
        return;

    Cart* cart = CURRENT_USER->cart;

    if (choice >= cart->item_count)
    {
        puts("Invalid item");
        return;
    }

    for (size_t i = choice; i < cart->item_count - 1; i++)
    {
        cart->items[i] = cart->items[i+1];
    }

    void* newMem = realloc(cart->items, sizeof(Item)*(cart->item_count - 1));
    if (newMem == NULL)
    {
        puts("Error removing item");
        return;
    }
    cart->item_count -= 1;
    cart->items = newMem;
}


void print_store()
{
    for (size_t i = 0; i < sizeof(ITEMS) / sizeof(Item); i++)
    {
        size_t dollars = ITEMS[i].cost / 100;
        size_t cents = ITEMS[i].cost % 100;
        printf("Item %lu: $%lu.%.02lu %s (%s)\n", ITEMS[i].id, dollars, cents, ITEMS[i].name, ITEMS[i].desc);
    }
}


void print_cart()
{
    Cart* cart = CURRENT_USER->cart;
    if (cart->item_count == 0)
    {
        puts("Cart is empty");
        return;
    }

    size_t total = 0;
    for (size_t i = 0; i < cart->item_count; i++)
    {
        Item item = cart->items[i];
        total += item.cost;
        size_t dollars = item.cost / 100;
        size_t cents = item.cost % 100;
        printf("Item %lu: %s for $%lu.%.02lu\n", i, item.name, dollars, cents);
    }
    printf("Total: $%lu.%.02lu\n", total / 100, total % 100);
}


void create_user()
{
    char username[16] = {0};
    printf("Username: ");
    int username_len = scanf("%15s", username);
    if (username_len <= 0)
    {
        puts("Invalid username");
        return;
    }

    char password[16] = {0};
    printf("Password: ");
    int password_len = scanf("%15s", password);
    if (password_len <= 0)
    {
        puts("Invalid password");
        return;
    }

    User* user = malloc(sizeof(User));
    user->admin = 0;
    user->username = malloc(16);
    memcpy(user->username, username, 16);
    user->password = malloc(16);
    memcpy(user->password, password, 16);
    user->cart = malloc(sizeof(Cart));
    memset(user->cart, 0, sizeof(Cart));
    user->nextUser = NULL;

    if (BASE_USER != NULL)
    {
        User* i = BASE_USER;
        while (i->nextUser != NULL)
        {
            i = i->nextUser;
        }
        i->nextUser = user;
    }
    else
    {
        BASE_USER = user;
    }

    CURRENT_USER = user;
}


void login()
{

    char username[16] = {0};
    printf("Username: ");
    int username_len = scanf("%15s", username);
    if (username_len <= 0)
    {
        puts("Invalid username");
        return;
    }

    char password[16] = {0};
    printf("Password: ");
    int password_len = scanf("%15s", password);
    if (password_len <= 0)
    {
        puts("Invalid password");
        return;
    }


    User* checkUser = BASE_USER;
    while (checkUser != NULL)
    {
        if (strcmp(checkUser->username, username) == 0 && strcmp(checkUser->password, password) == 0)
        {
            puts("Login succeeded");
            CURRENT_USER = checkUser;
            return;
        }
        checkUser = checkUser->nextUser;
    }
    puts("Login failed");
}


void admin_terminal()
{
    if (!CURRENT_USER->admin)
    {
        puts("Not an admin");
        return;
    }
    system("/bin/sh");
}


void checkout()
{
    puts("(Hmm, I don't have enough to pay for all of this... I'll put it all back.)");
    Cart* cart = CURRENT_USER->cart;
    if (cart->items != NULL)
    {
        free(cart->items);
    }
    memset(cart, 0, sizeof(Cart));
}


void menu()
{
    if (CURRENT_USER == NULL)
    {
        puts("1. Browse the shelves\n"
        "2. Open an account\n"
        "3. Log in to an existing account\n"
        "4. Exit\n"
        );
    }
    else
    {
        puts("1. Browse the shelves\n"
        "2. Add an item to your cart\n"
        "3. Remove an item from your cart\n"
        "4. Checkout\n"
        "5. Log out\n"
        "6. Exit\n");
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

        if (CURRENT_USER == NULL)
        {
            switch (choice)
            {
                case 1:
                {
                    print_store();
                    break;
                }
                case 2:
                    create_user();
                    break;
                case 3:
                    login();
                    break;
                case 4:
                    exit(0);
                    break;
                default:
                    puts("Invalid choice");
                    break;
            }
        }
        else
        {
            switch (choice)
            {
                case 1:
                    print_store();
                    break;
                case 2:
                    add_item();
                    break;
                case 3:
                    remove_item();
                    break;
                case 4:
                    checkout();
                    break;
                case 5:
                    CURRENT_USER = NULL;
                    break;
                case 6:
                    exit(0);
                case 7:
                    admin_terminal();
                    break;
                default:
                    puts("Invalid choice");
                    break;
            }
        }
    }
    return 0;
}
