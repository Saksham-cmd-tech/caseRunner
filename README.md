# ◆ CaseCraft

A terminal-based competitive programming test case runner — think Codeforces local tester, built with Python and Textual.

Tokyo Night theme · lazygit-style keybindings · per-file session persistence

---

## Installation

```bash
# 1. Clone / unzip the project
cd CaseCraft

# 2. Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Requires **Python 3.12+**.

---

## Usage

### Loading a file

Type the path to your `.py` solution in the **FILE** input at the top-left and press `Enter`.  
CaseCraft will load (or create) a session for that file automatically.

### Adding test cases

Press **`a`** to open the *Add Test Case* modal.  
Fill in:
- **Label / Name** — a short description (e.g. *Basic case*, *Edge: empty list*)
- **Input (stdin)** — what your program reads from stdin
- **Expected Output** — what your program should print

Press `ctrl+s` to save or `Escape` to cancel.

### Running tests

| Action | Key |
|---|---|
| Run **all** test cases | `ctrl+r` |
| Run **selected** test case | `Enter` (focus on TC list) |

### Managing test cases

| Action | Key |
|---|---|
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

Output comparison normalises whitespace: trailing spaces and blank lines at the end are ignored.

---

## Session System

- Every `.py` file gets its own **session** stored in `data/sessions.json`
- Switching to a different file automatically loads that file's test cases
- The last opened file is restored on the next launch
- Sessions survive app restarts — your test cases are always saved

---

## Project Structure

```
CaseCraft/
├── app.py              ← Textual app, UI composition, key bindings
├── runner.py           ← subprocess execution, verdict logic
├── models.py           ← TestCase, TestResult, Verdict, Session dataclasses
├── utils.py            ← session I/O, output normalisation, helpers
├── requirements.txt
├── README.md
├── data/
│   └── sessions.json   ← persisted sessions (auto-created)
└── widgets/
    ├── __init__.py
    ├── add_modal.py    ← Add / Edit test case modal
    └── diff_viewer.py  ← Expected vs Actual side-by-side viewer
```

---

## Screenshots

> _Run the app and enjoy the Tokyo Night TUI._

---

## Future Improvements

- [ ] Multi-language support (C++, Java, Go) via configurable run commands
- [ ] Stress tester — generate random inputs and compare two solutions
- [ ] Memory usage tracking alongside runtime
- [ ] Import test cases from a plain-text block (paste Codeforces samples)
- [ ] `ctrl+k` command palette
- [ ] Export results as a Markdown table
- [ ] Configurable timeout per test case
- [ ] Side-by-side character-level diff highlighting
