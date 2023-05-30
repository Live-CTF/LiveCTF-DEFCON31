#!/usr/bin/env python3

from generator_server import get_challenge_binary
from pathlib import Path

output_path = Path('/handout/samples')
output_path.mkdir(exist_ok=True)

for _ in range(20):
    sample_data, sample_password = get_challenge_binary()
    (output_path / f'{sample_password}.elf').write_bytes(sample_data)
