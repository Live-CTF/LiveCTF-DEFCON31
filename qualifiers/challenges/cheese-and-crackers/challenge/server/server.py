#!/usr/bin/env python3

import base64
import os
import select
import sys

if os.environ.get('LOCAL', False):
    from generator_dist import get_challenge_binary
else:
    from generator_server import get_challenge_binary

NUM_ROUNDS = 20
ROUND_TIMEOUT = 10.0

def do_round() -> bool:
    challenge = get_challenge_binary()
    if not challenge:
        raise RuntimeError('Failed to build challenge. Please contact an administrator.')
    challenge_data, challenge_password = challenge
    challenge_b64 = base64.b64encode(challenge_data).decode()

    print(f'Crackme: {challenge_b64}')
    # Using input() for prompt prints to stderr for non-TTY
    print('Password: ', end='', flush=True) 
    if not (stdin := select.select([sys.stdin], [], [], ROUND_TIMEOUT)[0]):
        return False
    
    user_password = stdin[0].readline().strip()
    return challenge_password == user_password


def do_game(num_rounds: int) -> bool:
    for round_number in range(num_rounds):
        print(f'Round {round_number+1}/{num_rounds}')
        round_result = do_round()
        if round_result:
            print('Correct!')
        else:
            print('Incorrect! Goodbye')
            return False
    return True


def main() -> int:
    try:
        flag = os.environ['FLAG']
    except KeyError:
        print('Flag environment variable not set')
        return 1

    if do_game(NUM_ROUNDS):
        print(f'Congratulations! Here is the flag: {flag}')
    else:
        print('You failed! Please try again')

    return 0

if __name__ == '__main__':
    sys.exit(main())
