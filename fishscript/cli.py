import argparse
from pathlib import Path

from .interpreter import FishScript
from .errors import FishScriptError
from . import __version__


def run_file(path: str):
    file_path = Path(path)

    if not file_path.exists():
        print(f"FishScript Error: file not found: {file_path}")
        raise SystemExit(1)

    code = file_path.read_text(encoding="utf-8")
    fish = FishScript()

    try:
        fish.run(code)
    except FishScriptError as error:
        print(f"FishScript Error:\n{error}")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="fishscript",
        description="FishScript - the world’s most unnecessary aquarium programming language."
    )

    parser.add_argument("--version", action="version", version=f"FishScript {__version__}")

    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Run a .fish file")
    run_parser.add_argument("file", help="Path to a .fish file")

    sub.add_parser("ide", help="Open the FishScript IDE")

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file)
    elif args.command == "ide":
        from .ide import main as ide_main
        ide_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
