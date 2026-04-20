import argparse
from pathlib import Path

from .interpreter import run_file

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="Path to the Cobalt file to execute.")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.file is None:
        print("Usage: python -m cobalt <file.co>")
        raise SystemExit(1)
    
    file = Path(args.file)

    run_file(file)