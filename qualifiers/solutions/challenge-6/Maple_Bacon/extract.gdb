catch syscall mmap
r < /dev/null
c
set $execpage=$rax
catch syscall write
c
disassemble $execpage,+0x100
