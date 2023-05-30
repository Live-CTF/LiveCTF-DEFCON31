
import random
from pathlib import Path
from typing import Optional, Tuple

pregenerated_path = Path('samples')

def get_challenge_binary() -> Optional[Tuple[bytes, str]]:
    # Note: This function is different on the server
    # In this version, you are simply given one of a few
    # pre-generated samples. On the real server these samples
    # will be dynamically generated but all samples will follow
    # the same general structure.
    print('Building challenge binary')
    samples = list(pregenerated_path.glob('*.elf'))
    challenge_binary_path = random.choice(samples)
    password = challenge_binary_path.stem
    challenge_binary = challenge_binary_path.read_bytes()
    return challenge_binary, password
