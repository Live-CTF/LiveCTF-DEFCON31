from ptrlib import *
import base64

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 # os.getenv('PORT', 31337)

def decode(buf, KEY: bytes):
    assert len(KEY) == 0x20
    buf2 = b""
    arr = [i for i in range(0x100)]

    j = 0
    for i in range(0x100):
        tmp = arr[i]
        j = (j + tmp + KEY[i & 0x1f]) % 0x100
        arr[i] = arr[j]
        arr[j] = tmp

    _i = 0
    for i in range(0xff):
        _i = (_i + 1) % 0x100
        tmp = arr[_i]
        j = (j + tmp) % 0x100
        arr[_i] = arr[j]
        arr[j] = tmp
        buf2 += bytes([buf[i] ^ arr[(tmp + arr[_i]) % 0x100]])
    return buf2

# stream = Process("./challenge", cwd="handout")
stream = Socket(HOST, PORT)
sock = stream

import re
import subprocess
import glob

for a in range(20):
  print(sock.recvuntil("Crackme: "))
  data = sock.recvuntil("Password: ")
  data = data.split(b"\n")[0]
  data = base64.b64decode(data)

  f = open("/tmp/ud12345","wb")
  f.write(data)
  f.close()
  output = subprocess.check_output(["objdump", "-S", "-M", "intel", "/tmp/ud12345"])
  go = False
  for line in output.split(b"\n"):
        if go:
            r = re.findall(b"al,BYTE PTR \[rsi\+(0x[0-9a-f]+)\]", line)
            break
        if b"al,r8b" in line:
            go = True

  addr = int(r[0], 16) - 0x200000
  with open("/tmp/ud12345", "rb") as f:
        f.seek(addr)
        key = f.read(0x20)
        f.seek(0x348)
        binary = f.read(0x100)

  print(key)
  q = decode(binary,key)
  q = disasm(q)
  ans = b""
  for i in q:
    if "cmp BYTE" in i[1]:
      ans += bytes( [int(i[1].split(",")[-1],16)] )
  print(ans)
  sock.send(ans + b"\n")


from time import sleep
sleep(1)
#stream.send(b'/home/livectf/submitter\n')

for i in range(100):
    try:
        print(stream.recvline(timeout=1))
    except TimeoutError:
        break

stream.close()

