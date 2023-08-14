import argparse

from pwn import *
from z3 import BitVec, Solver, sat, UDiv, URem
import binaryninja as bn

PATH = '../challenge/build/challenge'
bv = bn.load(PATH)

# Probably a good way to statically extract this,
# but it's not randomized for now, so just run it
# once and dump the order

#50, null seed
#order = [26, 41, 32, 18, 45, 48, 8, 35, 44, 31, 10, 30, 24, 1, 12, 13, 40, 0, 43, 47, 27, 42, 4, 14, 49, 36, 6, 19, 5, 11, 7, 37, 34, 28, 21, 46, 38, 20, 16, 2, 17, 15, 3, 22, 25, 29, 23, 9, 39, 33]

#40, null seed
order = [8, 4, 13, 24, 21, 19, 14, 17, 0, 31, 30, 26, 37, 39, 33, 27, 35, 28, 15, 11, 16, 29, 34, 12, 1, 25, 7, 32, 18, 2, 38, 36, 6, 20, 10, 5, 9, 3, 22, 23]

#lol, this code is so brittle but it works during testing
last_puts = list(bv.get_functions_by_name("puts")[0].caller_sites)[-1]
correct = last_puts.hlil.il_basic_block.incoming_edges[0].source[-1].condition.right.value.value
print(f"correct value: {hex(correct)}")

# Define operations
def add(x, y):
    return x + y

def sub(x, y):
    return x - y

def mul(x, y):
    return x * y

def div(x, y):
    if y == 0:
        return x  # Avoid division by zero.
    return UDiv(x, y)

def mod(x, y):
    return URem(x, y)

steps = []
for index in order:
    f = bv.get_functions_by_name(f"function_{index}")[0]
    il = next(f.hlil.instructions).src[0]
    match il.operation:
        case bn.HighLevelILOperation.HLIL_ADD:
            op = add
        case bn.HighLevelILOperation.HLIL_SUB:
            op = sub
        case bn.HighLevelILOperation.HLIL_MUL:
            op = mul
        case bn.HighLevelILOperation.HLIL_DIVU:
            op = div
    if isinstance(il.left, bn.Constant):
        constant = il.left.constant
    else:
        constant = il.right.constant
    steps.append((op, constant))

initial_value = BitVec("initial_value", 64)
result = [BitVec(f"result_{i}", 64) for i in range(len(steps)+1)]
# Define the computation using the initial_value
s = Solver()
s.add(result[0] == initial_value)
for i in range(len(steps)):
    op, const = steps[i]
    #print(op, const)
    s.add(result[i+1] == op(result[i], const))

# Constraint for the final value
s.add(result[len(steps)] == correct)
print(repr(s))
# Check and get the solution
if s.check() == sat:
    m = s.model()
    solution = m.evaluate(initial_value)
    print(f"Initial value to achieve target: {solution}")
else:
    print("No solution found!")

'''
r.recvuntil(b'Enter the initial value: ')
r.sendline(str(value))
r.interactive()
'''
