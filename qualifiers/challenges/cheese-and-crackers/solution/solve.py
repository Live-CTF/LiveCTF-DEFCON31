#!/usr/bin/env python3

import base64
import re
import lief
import tempfile
import subprocess
from pathlib import Path
from pwn import *
from capstone import *

HOST = 'localhost'
PORT = 31337

GDB_TEMPLATE = '''
break *%#x
commands
print $%s
dump binary memory %s/chall_code.dat $%s $%s+0x1000
end

run < /dev/null
'''

io = remote(HOST, PORT)

with tempfile.TemporaryDirectory() as tmpdirname:
    tmppath = Path(tmpdirname)
    while True:
        round_indicator = io.recvline().decode().strip()
        round_match = re.match('Round (\d+)/(\d+)', round_indicator) 
        cur_round, max_round = int(round_match[1]), int(round_match[2])
        log.info('Round %d/%d', cur_round, max_round)

        io.recvline().decode().strip() # "Building challenge binary"

        line = io.recvline().decode().strip()
        if line.startswith('Challenge password: '):
            password = line.split(':', 1)[-1].strip()
            log.info('Cheat password: %s', password)
            line = io.recvline().decode().strip()

        if not line.startswith('Crackme: '):
            log.error('Unexpected start of line: "%s"', line[:20])

        binary_b64 = line.split(':', 1)[-1]
        binary_data = base64.b64decode(binary_b64)
        chall_tmp_path = tmppath / Path('chall_tmp')
        chall_tmp_path.write_bytes(binary_data)
        chall_tmp_path.chmod(0o755)

        elf = lief.ELF.parse(str(chall_tmp_path))
        log.info('Entry: %x', elf.entrypoint)
        code = bytes(elf.get_content_from_virtual_address(elf.entrypoint, 0x1000))
        log.info('Code: %s', code[:100].hex())

        md = Cs(CS_ARCH_X86, CS_MODE_64)
        for i in md.disasm(code, elf.entrypoint):
            if i.mnemonic == 'call' and not i.op_str.startswith('0x'):
                #print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
                break_addr = i.address
                target_register = i.op_str
                break
        log.info('Breaking at %#x (%s)', break_addr, target_register)

        gdb_cmds_path = tmppath / Path('gdb_cmds.txt')
        dumped_code = tmppath / Path('chall_code.dat')
        gdb_cmds = GDB_TEMPLATE.strip() % (break_addr, target_register, str(tmppath), target_register, target_register)
        gdb_cmds_path.write_text(gdb_cmds)

        subprocess.check_call(['gdb', '-batch', '-x', str(gdb_cmds_path), str(chall_tmp_path)], stdout=subprocess.DEVNULL)
        dumped_code_data = dumped_code.read_bytes()

        gdb_cmds_path.unlink()
        dumped_code.unlink()
        
        extracted_password = []
        md = Cs(CS_ARCH_X86, CS_MODE_64)
        for i in md.disasm(dumped_code_data, elf.entrypoint):
            #print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
            if i.mnemonic == 'cmp':
                extracted_password.append(int(i.op_str.split(',')[-1].strip(), 16))
            if i.mnemonic == 'ret':
                break

        password = bytes(extracted_password[1:]).decode()
        
        io_test = process(str(chall_tmp_path))
        io_test.sendline(password.encode())
        test_res = io_test.recvline().decode().strip()
        log.info('Test result: %s', test_res)
        io_test.close()

        chall_tmp_path.unlink()

        io.recvuntil(b'Password: ')
        io.sendline(password.encode())
        submit_res = io.recvline().decode().strip()
        log.info('Status: %s', submit_res)

        if cur_round == max_round:
            break

io.interactive()
