from pwn import *
from capstone import *
import re

lmao = re.compile(r"cmp    BYTE PTR \[rax(\+.+)?\], (?P<hex>.+)$", re.IGNORECASE | re.MULTILINE)
lmao2 = re.compile(r"add    al, BYTE PTR \[rsi\+(?P<hex>.+)\]", re.MULTILINE)

context.arch = "amd64"

context.log_level = 'info'

def solve(chal_bin):
    with open("/tmp/lmao.bin", "wb") as f:
        f.write(chal_bin)
    binary_file = ELF("/tmp/lmao.bin")

    DATA = binary_file.read(0x00200348, 0x1000)

    search_for = bytes.fromhex("44 04 80 48 ff c0 eb ef 31 c0 31 c9 48 81 f9 00 01 00 00 74 28 44 8a 44 0c 80 89 ce 83 e6 1f 44 00 c0 02 86")

    for loc in binary_file.search(bytes(search_for)):
        ptr = binary_file.read(loc + len(search_for), 4)
        LOOKUP = binary_file.read(int.from_bytes(ptr, 'little'), 0x20)
        break

    def shuffle(data: list[int]):
        nums = list(range(256))

        pos = 0
        for i in range(256):
            b = nums[i]
            pos = (pos + b + LOOKUP[i & 0x1f]) & 0xff
            nums[i] = nums[pos]
            nums[pos] = b

        pos_ = 0
        for i in range(255):
            pos_ = (pos_ + 1) & 0xff
            b = nums[pos_ ]
            pos = (pos + b) & 0xff
            nums[pos_ ] = nums[pos]
            nums[pos] = b
            data[i] = data[i] ^ nums[(b + nums[pos_ ]) & 0xff]

        return data

    shuffled = shuffle(list(DATA))
    # print(' '.join([hex(x) for x in LOOKUP]))

    # disassemble shellcode
    shellcode = bytes(shuffled)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    password = ''.join([chr(int(i.op_str.split(',')[1].strip(), 0)) for i in md.disasm(shellcode, 0) if i.mnemonic == 'cmp']).strip()

    print(password)
    return password

def solve_old(chal_bin: bytes):
    instr_target = 0x1762
    instr_data = chal_bin[instr_target:instr_target+6]
    listing = disasm(instr_data)
    m = lmao2.search(listing)
    sbox_addr = int(m.group("hex"), 0)
    sbox_addr -= 0x200000

    # sbox_addr = 0x0000e1b
    code_addr = 0x0000348
    sbox = chal_bin[sbox_addr:sbox_addr + 32]
    code = chal_bin[code_addr:code_addr + 255]
    LOOKUP = sbox
    data = bytearray(code)
    
    nums = list(range(256))

    pos = 0
    for i in range(256):
        b = nums[i]
        pos = (pos + b + LOOKUP[i & 0x1f]) & 0xff
        nums[i] = nums[pos]
        nums[pos] = b

    pos_ = 0
    for i in range(255):
        pos_ = (pos_ + 1) & 0xff
        b = nums[pos_ ]
        pos = (pos + b) & 0xff
        nums[pos_ ] = nums[pos]
        nums[pos] = b
        data[i] = data[i] ^ nums[(b + nums[pos_ ]) & 0xff]

    listing = disasm(data)
    hehe = lmao.findall(listing)
    ret = ""
    for (_, val) in hehe:
        car = int(val, 0)
        ret += chr(car)
    print(ret)
    return ret

if __name__ == "__main__":
    solve(read(sys.argv[1]))