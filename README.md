# ◆ CaseCraft

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/Saksham-cmd-tech/caseRunner)
[![PyPI](https://img.shields.io/pypi/v/casecraft?color=blue)](https://pypi.org/project/casecraft/)

**Source:** [https://github.com/Saksham-cmd-tech/caseRunner.git](https://github.com/Saksham-cmd-tech/caseRunner.git)

A terminal-based test case runner for developers. CaseCraft provides a sleek, Tokyo Night-themed interface to test edge cases, validate function outputs, and track your code's behavior—right from the terminal.

Built with Python and Textual, it features lazygit-style keybindings, native terminal transparency, a beautiful boot sequence, and per-file session persistence.

---

## Features

- **Dynamic Boot Sequence**: Hacker-style splash screen that automatically checks PyPI for version updates in the background.
- **Native Transparency**: Automatically inherits your terminal's background color and opacity.
- **Cross-Platform Execution**: Safely evaluates the correct executable environments (e.g. `python3` vs `python`) across macOS, Linux, and Windows.
- **Local Persistence**: All your test cases are saved locally inside a `.casecraft/` folder in your project.

---

## Installation

CaseCraft is available via pip:

```bash
pip install casecraft
```

Requires **Python 3.10+**.

---

## Usage

### 1. Initialization
To start using CaseCraft in your project, simply run the CLI command:
```bash
casecraft init
```
This will generate a hidden `.casecraft/` folder in your current directory where all test case data will be safely persisted.

### 2. Launching the App
Open the dashboard by running:
```bash
casecraft
```

### 3. Loading a File
Press **`p`** to open the *Directory Tree* modal. Navigate through your project files using the arrow keys and press `Enter` to select your source file (e.g. `src/main.py`).  
CaseCraft will load your file and assign an empty test suite to it.

### 4. Adding Test Cases
Press **`a`** to open the *Add Test Case* modal.  
Fill in:
- **Label / Name** — a short description (e.g. *Basic case*, *Edge: empty list*)
- **Input (stdin)** — the arguments or data you want to pipe into the program
- **Expected Output** — the output you want the program to print

Press `ctrl+s` to save or `Escape` to cancel.

### 5. Running Tests

| Action | Key |
|---|---|
| Run **all** test cases | `space` |

### 6. Managing Test Cases

| Action | Key |
|---|---|
| Search | `/` |
| Add | `a` |
| Edit selected | `e` |
| Delete selected | `d` |
| Switch panels | `Tab` |
| Quit | `q` |

---

## Verdicts

| Badge | Meaning |
|---|---|
| `AC` | Accepted — output matches expected |
| `WA` | Wrong Answer — output differs |
| `TLE` | Time Limit Exceeded — ran longer than 2 seconds |
| `RE` | Runtime Error — non-zero exit code or exception |

Output comparison normalizes whitespace: trailing spaces and blank lines at the end are ignored.

---

## Session System

- Every `.py` file gets its own **session** stored in `.casecraft/sessions.json`.
- Switching to a different file automatically loads that file's test cases.
- The last opened file is restored on the next launch.
- Sessions survive app restarts — your test cases are always saved locally to your project workspace.

---

## Project Structure

```
CaseCraft/
├── pyproject.toml
├── README.md
├── src/
│   └── casecraft/
│       ├── cli.py              ← CLI initialization logic
│       ├── app.py              ← Textual app, UI composition
│       ├── runner.py           ← subprocess execution
│       ├── models.py           ← Data models
│       ├── utils.py            ← session I/O, helpers
│       └── widgets/
│           └── add_modal.py    ← Add / Edit test case modal
```

---

## Screenshots

> _Run the app and enjoy the Tokyo Night TUI._

---

## About & Support

**CaseCraft** is built and maintained by Saksham. 

If you encounter any bugs, have feature requests, or want to contribute, please visit the [Issue Tracker](https://github.com/Saksham-cmd-tech/caseRunner/issues). 

---

## Future Improvements

- [ ] Multi-language support (Node.js, Go, Rust) via configurable run commands
- [ ] Environment variable injection per test case
- [ ] Memory usage tracking alongside runtime
- [ ] `ctrl+k` command palette
- [ ] Export results as a Markdown or JSON report
- [ ] Configurable timeout per test case
- [ ] Side-by-side character-level diff highlighting
