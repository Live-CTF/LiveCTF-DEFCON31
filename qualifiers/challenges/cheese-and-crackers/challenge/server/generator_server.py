
import subprocess
import hashlib
import random
from pathlib import Path
from typing import Optional, Tuple

def get_challenge_binary() -> Optional[Tuple[bytes, str]]:
    password = random.randbytes(16).hex()

    print('Building challenge binary')
    try:
        subprocess.check_call(['/usr/local/zig/zig', 'build', '-Doptimize=ReleaseSmall', f'-Dpassword={password}'], cwd='/generator', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    build_path = Path('/generator/zig-out/bin/') / f'challenge-{password_hash}-x86_64'
    build_path_validator = Path('/generator/zig-out/bin/') / f'validator-{password_hash}-x86_64'

    challenge_data = build_path.read_bytes()
    build_path.unlink()
    build_path_validator.unlink()

    return challenge_data, password
