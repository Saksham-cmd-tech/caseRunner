"""
cli.py — Command-Line Interface for CaseRunner.
"""

import argparse
import sys

from caserunner.utils import is_initialized, initialize_workspace
from caserunner.app import CaseRunnerApp

def main():
    parser = argparse.ArgumentParser(description="CaseRunner - TUI for algorithmic test cases.")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a CaseRunner workspace in the current directory.")

    args = parser.parse_args()

    if args.command == "init":
        if is_initialized():
            print("CaseRunner is already initialized in this directory (.caserunner exists).")
        else:
            initialize_workspace()
            print("Successfully initialized CaseRunner in .caserunner/")
        sys.exit(0)

    # If no command provided, run the TUI
    app = CaseRunnerApp()
    app.run()

if __name__ == "__main__":
    main()
