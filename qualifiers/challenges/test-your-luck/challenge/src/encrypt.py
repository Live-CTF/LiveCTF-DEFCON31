import subprocess

from dataclasses import dataclass

@dataclass
class FunctionInfo:
    name: str
    start: int
    length: int


def get_encrypt_function_info() -> list[FunctionInfo]:
    cmd = "objdump -t build/challenge"
    output = subprocess.run(cmd.split(), check=True, capture_output=True)

    info = []

    for i in output.stdout.decode().strip().splitlines():
        line_split = i.split()
        if len(line_split) != 6:
            continue
        if line_split[2] != 'F':
            # not a function
            continue
        if line_split[3] != 'encrypted':
            # not a function
            continue
        function_name = line_split[5]
        print(i.split())
        info.append(FunctionInfo(
            name=function_name,
            start=int(line_split[0], 16),
            length=int(line_split[4], 16)
        ))
    return info


with open('build/challenge', 'rb') as f:
    file_contents = bytearray(f.read())

# with open('build/challenge_unencrypted', 'wb') as f:
#     f.write(file_contents)

for func_info in get_encrypt_function_info():
    ptxt = file_contents[func_info.start:func_info.start + func_info.length]
    ctxt = bytes(i^0x41 for i in ptxt)
    file_contents[func_info.start:func_info.start + func_info.length] = ctxt
    print(ptxt.hex())
    print(func_info)

with open('build/challenge', 'wb') as f:
    f.write(file_contents.replace(b"encrypted", b"\x00"*9))
