from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    src_dir = Path(__file__).parent / "src"
    with tempfile.TemporaryDirectory() as build_dir:
        with open(Path(build_dir) / "link.ld", "wb") as f:
            while True:
                conts = sys.stdin.buffer.readline()
                if conts.strip() == b"":
                    break
                f.write(conts)

        try:
            proc = subprocess.Popen(['cmake', '-B', build_dir], cwd=src_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(timeout=15)
        finally:
            sys.stdout.buffer.write(stdout)
            sys.stdout.buffer.write(stderr)
            stdout, stderr = None, None

        try:
            proc = subprocess.Popen(['cmake', '--build', build_dir], cwd=src_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(timeout=15)
        finally:
            sys.stdout.buffer.write(stdout)
            sys.stdout.buffer.write(stderr)
            stdout, stderr = None, None

        if not (Path(build_dir) / "main").exists():
            print("Compile failed, aborting.")
            return

        try:
            proc = subprocess.Popen([build_dir + "/main"], cwd="/home/livectf", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(timeout=15)
        finally:
            proc.kill()
            sys.stdout.buffer.write(stdout)
            sys.stdout.buffer.write(stderr)
            stdout, stderr = None, None


if __name__ == '__main__':
    main()
