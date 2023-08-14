import random

# Define operations
operations = ['+=', '-=', '*=', '/=']
max_functions = 40
primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]

# Generate C file
with open('program.c', 'w') as f:
    f.write('#include <stdio.h>\n')
    f.write('#include <stdlib.h>\n')
    f.write('#include <time.h>\n\n')

    for i in range(max_functions):
        op = random.choice(operations)
        if op == "/=":
            constant = random.choice(primes)
        else:
            constant = random.randint(1<<31, 1<<63)
        f.write('unsigned long long int function_{0}(unsigned long long int value) {{\n'.format(i))
        f.write('    value {0} {1};\n'.format(op, constant))
        f.write('    return value;\n')
        f.write('}\n\n')

    f.write('void init(void) {');
    f.write('    setvbuf(stdin, NULL, _IONBF, 0);');
    f.write('    setvbuf(stdout, NULL, _IONBF, 0);');
    f.write('}');

    # Generate main function
    f.write('int main() {\n')
    f.write('    init();\n')
    # If too easy, seed with time, too hard, uncomment the ordering below.
    f.write('    srand(0);\n')  # Seed the random number generator
    f.write(f'    int order[{max_functions}];\n')
    f.write(f'    for (int i = 0; i < {max_functions}; i++) order[i] = i;\n')
    f.write(f'    for (int i = {max_functions-1}; i > 0; i--) {{\n')
    f.write('        int j = rand() % (i + 1);\n')  # Fisher-Yates shuffle
    f.write('        int temp = order[i];\n')
    f.write('        order[i] = order[j];\n')
    f.write('        order[j] = temp;\n')
    f.write('    }\n\n')

    # Comment out below line for slightly more difficulty
    #f.write(f'    for (int i = 0; i < {max_functions}; i++) printf("%d, ", order[i]);\n')

    f.write('    printf("Enter the initial value: ");\n')
    f.write('    unsigned long long int value;\n')
    f.write('    scanf("%llu", &value);\n')
    f.write(f'    for (int i = 0; i < {max_functions}; i++) {{\n')
    f.write('        switch(order[i]) {\n')
    for i in range(max_functions):
        f.write('            case {0}:\n'.format(i))
        f.write('                value = function_{0}(value);\n'.format(i))
        f.write('                break;\n')
    f.write('        }\n')
    f.write('    }\n')
    # Compile once, run with desired input, copy correct value, rebuild just the c without
    # re-running the generator
    f.write('    if (value == -1) { // Fixup after generation \n')
    f.write('        printf("Congratulations! Your initial value has produced the correct final value!\\n");\n')
    f.write('        system("/bin/sh");\n')
    f.write('    } else {\n')
    f.write('        printf("Try again. Final value is not correct.\\n%llx\\n",value);\n')
    #f.write('        printf("That\'s incorrect, try again.");\n')
    f.write('    }\n')
    f.write('    return 0;\n')
    f.write('}\n')