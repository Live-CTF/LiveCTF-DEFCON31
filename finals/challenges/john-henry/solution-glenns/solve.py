import argparse
import codecs
import leb128
import math
import threading
import traceback

from pwn import *

context.log_level = 'debug'
# context.log_level = 'error'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

# r = process(['./challenge'])
# gdb.attach(r, f'''
# c
# ''')


"""
0x7ffdf2d30a38: 0x0000000000000001      0x0000000400000008
0x7ffdf2d30a48: 0x000000180000000d      0x0000001300000015
0x7ffdf2d30a58: 0x000000110000000e      0x0000001f00000000
0x7ffdf2d30a68: 0x0000001a0000001e      0x0000002700000025
0x7ffdf2d30a78: 0x0000001b00000021      0x0000001c00000023
0x7ffdf2d30a88: 0x0000000b0000000f      0x0000001d00000010
0x7ffdf2d30a98: 0x0000000c00000022      0x0000001900000001
0x7ffdf2d30aa8: 0x0000002000000007      0x0000000200000012
0x7ffdf2d30ab8: 0x0000002400000026      0x0000001400000006
0x7ffdf2d30ac8: 0x000000050000000a      0x0000000300000009
0x7ffdf2d30ad8: 0x0000001700000016      0x0000000000000000
0x7ffdf2d30ae8: 0x0000000400000000      0x0000000000000001
0x7ffdf2d30af8: 0x0000002800000000      0x0000000000000001

00000004
00000008
00000018
0000000d
00000013
00000015
00000011
0000000e
0000001f
00000000
0000001a
0000001e
00000027
00000025
0000001b
00000021
0000001c
00000023
0000000b
0000000f
0000001d
00000010
0000000c
00000022
00000019
00000001
00000020
00000007
00000002
00000012
00000024
00000026
00000014
00000006
00000005
0000000a
00000003
00000009
00000017
00000016
"""

def function_0(arg1):
    return z3.UDiv(arg1, 0xd)
def function_1(arg1):
    return arg1 + 0x690c58868f42a63e
def function_2(arg1):
    return z3.UDiv(arg1, 0xd)
def function_3(arg1):
    return z3.UDiv(arg1, 0x65)
def function_4(arg1):
    return arg1 * 0x23153d4b0f894b44
def function_5(arg1):
    return arg1 - 0x2a28a42fad4fb2a
def function_6(arg1):
    return arg1 - 0x6ab7db1382fa2929
def function_7(arg1):
    return arg1 - 0x524bdca920b0dda7
def function_8(arg1):
    return arg1 * 0x2dd541b015b63b53
def function_9(arg1):
    return arg1 * 0x11b21fde606d4a1d
def function_10(arg1):
    return arg1 * 0x1971f12a08beede9
def function_11(arg1):
    return arg1 * 0x3adc3ad2dad2af95
def function_12(arg1):
    return arg1 + 0x1b25c29f7e4676d1
def function_13(arg1):
    return arg1 * 0x48e5037bca027a43
def function_14(arg1):
    return z3.UDiv(arg1, 0x49)
def function_15(arg1):
    return arg1 + 0x689a9eb4fa6cae27
def function_16(arg1):
    return arg1 + 0x5cab216fc38e1ee3
def function_17(arg1):
    return arg1 + 0x43c3540aadec6f46
def function_18(arg1):
    return z3.UDiv(arg1, 0x3b)
def function_19(arg1):
    return arg1 - 0x3cbdb5c969b69f52
def function_20(arg1):
    return arg1 + 0x25abcf1d49084542
def function_21(arg1):
    return z3.UDiv(arg1, 0x3d)
def function_22(arg1):
    return arg1 * 0x6af2dfd834ac9100
def function_23(arg1):
    return arg1 * 0x1afd8b89ea2a4e53
def function_24(arg1):
    return arg1 + 0x7ef932205fc32024
def function_25(arg1):
    return arg1 * 0x6399bde48df72dd7
def function_26(arg1):
    return arg1 + 0x618bcd93ca65db6c
def function_27(arg1):
    return arg1 + 0x3f572d6fe6276368
def function_28(arg1):
    return arg1 + 0x24ac15629fc3c49
def function_29(arg1):
    return arg1 - 0x5f2fa7009a06140e
def function_30(arg1):
    return arg1 * 0x31a824051660ed82
def function_31(arg1):
    return z3.UDiv(arg1, 0x89)
def function_32(arg1):
    return arg1 - 0x98e2c4ae604c46e
def function_33(arg1):
    return arg1 - 0x4a7733d93a03514a
def function_34(arg1):
    return z3.UDiv(arg1, 0x65)
def function_35(arg1):
    return arg1 - 0x6e341c17a0818b89
def function_36(arg1):
    return z3.UDiv(arg1, 0x59)
def function_37(arg1):
    return arg1 * 0xf2fafa3a68bff5c
def function_38(arg1):
    return arg1 * 0x48901084b20923d7
def function_39(arg1):
    return z3.UDiv(arg1, 5)

funcs = [function_0, function_1, function_2, function_3, function_4, function_5, function_6, function_7, function_8, function_9, function_10, function_11, function_12, function_13, function_14, function_15, function_16, function_17, function_18, function_19, function_20, function_21, function_22, function_23, function_24, function_25, function_26, function_27, function_28, function_29, function_30, function_31, function_32, function_33, function_34, function_35, function_36, function_37, function_38, function_39]
order = [
0x08,
0x04,
0x0d,
0x18,
0x15,
0x13,
0x0e,
0x11,
0x00,
0x1f,
0x1e,
0x1a,
0x25,
0x27,
0x21,
0x1b,
0x23,
0x1c,
0x0f,
0x0b,
0x10,
0x1d,
0x22,
0x0c,
0x01,
0x19,
0x07,
0x20,
0x12,
0x02,
0x26,
0x24,
0x06,
0x14,
0x0a,
0x05,
0x09,
0x03,
0x16,
0x17,
]


import z3

s = z3.Solver()

var = [z3.BitVec(f"x{i}", 64) for i in range(len(order) + 1)]
s.add(var[-1] == 0x6fd86066670e9100)

for i in reversed(range(len(order))):
    s.add(var[i + 1] == funcs[order[i]](var[i]))
    # print(s.assertions)
    # print(s.check())
    # print(s.model())


try:
    print(s.assertions)
    print(s.check())
    print(s.model())

    sol = str(s.model()[var[0]])
    print(sol)

    r.sendlineafter(b'Enter the initial value: ', sol.encode())
except:
    traceback.print_exc()

r.interactive()
