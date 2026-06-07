"""
cli.py — Command-Line Interface for CaseCraft.
"""

import argparse
import sys

from casecraft.utils import is_initialized, initialize_workspace
from casecraft.app import CaseCraftApp

def main():
    parser = argparse.ArgumentParser(description="CaseCraft - TUI for algorithmic test cases.")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a CaseCraft workspace in the current directory.")

    args = parser.parse_args()

    if args.command == "init":
        if is_initialized():
            print("CaseCraft is already initialized in this directory (.casecraft exists).")
        else:
            initialize_workspace()
            print("Successfully initialized CaseCraft in .casecraft/")
        sys.exit(0)

    # If no command provided, run the TUI
    app = CaseCraftApp()
    app.run()

if __name__ == "__main__":
    main()
