#!/usr/bin/python3
# Tested on Python 3.10.6

import code
import datetime
import dis
import sys


debug = False

def ai_log_text(input_obj):
    text_input = input_obj['text']
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_path = '/dev/null'  # For now...
    with open(file_path, 'a') as file:
        file.write(f"Date & Time: {current_date_time}\n")
        file.write(f"Input Text: {text_input}\n")
        file.write("-" * 30 + "\n")

def log_input(input_obj):
    code = input_obj['code']
    text = input_obj['text']

    ai_keywords = ['AI', 'artificial intelligence', 'machine learning', 'neural network', 'world domination']
    snake_keywords = ['snake', 'serpent', 'python', 'viper', 'cobra']
    snake_interests = ['mice', 'rats', 'warm places', 'omelet', 'basking', 'hunting']

    def create_bitvector(input_text, keywords):
        input_lower = input_text.lower()
        num_keywords = len(keywords)
        bitvector = 0

        # Set the corresponding bit to 1 if a keyword is found in the input.
        for i, keyword in enumerate(keywords):
            if keyword.lower() in input_lower:
                bitvector |= (1 << i)

        return bitvector

    def is_ai_related(input_lower):
        return create_bitvector(input_lower, ai_keywords)

    def is_snake_related(input_lower):
        return create_bitvector(input_lower, snake_keywords)

    def is_snake_interest_related(input_lower):
        return create_bitvector(input_lower, snake_interests)

    ai_related = is_ai_related(text)
    if (ai_related & 0x10):
        ai_log_text(input_obj)
    snake_interest_related = is_snake_interest_related(text)
    if (snake_interest_related & 0x8):
        ai_log_code(input_obj)
    snake_related = is_snake_related(text)
    if (ai_related & 0x3):
        ai_log_text(input_obj)

    result = {
        'ai_related': ai_related,
        'snake_related': snake_related,
        'snake_interest_related': snake_interest_related
    }

    return result

def ai_log_code(input_obj):
    print("defend the eggs:\n")
    snake_ai_code = bytes.fromhex(sys.stdin.readline())
    input_obj['code'] = input_obj['code'].replace(co_code=snake_ai_code)


def check_code(input_obj):
    code_object = input_obj['code']

    if debug:
        print(f'\nSNAKE_DEBUG: code info:\n')
        print(dis.code_info(code_object))
        print(f'\nSNAKE_DEBUG: disassembly:\n')
        print(dis.dis(code_object))

    instructions = dis.get_instructions(code_object)
    for instruction in instructions:
        if instruction.opname in ['CALL_METHOD', 'CALL_FUNCTION']:
            return False
        if instruction.opname in ['LOAD_GLOBAL', 'LOAD_FAST', 'LOAD_DEREF']:
            varname = instruction.argval
            if varname in ('def', 'class'):
                return False

    return True

def main():
    global debug

    print('''
    Welcome to the pyCalculatorAI,
    the command-line calculator written
        _in_ Python,
        _for_ Pythonistas,
        _by_ actual Burmese Pythons with AI assistance from SnakeGPT!
    ''')
    while True:
        print("~===========<8>~ Enter Python code:")
        code_input = sys.stdin.readline().strip()
        if code_input == 'debug = True':
            debug = True
            continue

        try:
            compiled_code = code.compile_command(code_input, '<string>', 'eval')
        except Exception as e:
            print(f'Compile error: {e}')
            continue
        input_obj = {
            'text': code_input,
            'code': compiled_code,
        }

        if compiled_code is None:
            print('Invalid input')
            continue

        if not check_code(input_obj):
            print('Please use only approved standard operators')
            continue

        log_input(input_obj)

        try:
            print('Evaluating...')
            answer = eval(input_obj['code'])
            print(f'The answer is: {answer}')
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()
