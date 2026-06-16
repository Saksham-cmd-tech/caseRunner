"""
cli.py — Command-Line Interface for CaseCraft.
"""

import argparse
import sys
import os
from pathlib import Path

from casecraft.utils import is_initialized, initialize_workspace, load_sessions
from casecraft.app import CaseCraftApp

def main():
    parser = argparse.ArgumentParser(description="CaseCraft - Terminal test case manager.")
    parser.add_argument(
        "target", 
        nargs="?", 
        help="Source file to run headlessly, or 'init' to initialize a workspace"
    )

    args = parser.parse_args()

    if args.target == "init":
        if is_initialized():
            print("CaseCraft is already initialized in this directory (.casecraft exists).")
        else:
            initialize_workspace()
            print("Successfully initialized CaseCraft in .casecraft/")
        sys.exit(0)
    elif args.target:
        # User passed a filename, so run headlessly
        file_path = str(Path(args.target).resolve())
        sessions = load_sessions()
        
        if file_path not in sessions or not sessions[file_path].test_cases:
            from rich.console import Console
            console = Console()
            console.print(f"[bold yellow]No test cases found for {args.target}[/bold yellow]")
            console.print("Launch the UI using `casecraft` to add some test cases first.")
            sys.exit(1)
            
        from casecraft.headless import run_headless
        run_headless(file_path, sessions[file_path].test_cases)
        sys.exit(0)

    # If no arguments, run the TUI
    app = CaseCraftApp()
    app.run()

if __name__ == "__main__":
    main()
