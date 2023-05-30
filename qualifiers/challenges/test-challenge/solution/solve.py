from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))

r.recvline_contains(b'Give me input: ')
r.sendline(b'WIN')
r.recvline_contains(b'You sent: ')
r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
