# Personal Finance Manager

A desktop personal finance application built with Python and PyQt6.

Track accounts, import bank statements, categorise transactions with AI, monitor budgets, plan goals, and export reports — all stored locally with no cloud dependency.

---

## Features

| Feature | Details |
|---------|---------|
| **Accounts** | Checking, savings, credit cards, investments, loans |
| **Transactions** | Manual entry or import from PDF, CSV, XLSX, DOCX |
| **AI Categorisation** | Ollama (local LLM) suggests categories automatically |
| **Dashboard** | Net worth, monthly spending, budget status, recent activity |
| **Budgets** | Monthly limits per category with warning / exceeded alerts |
| **Goals** | Savings, debt payoff (snowball / avalanche), retirement projections |
| **Investments** | Holdings tracker with allocation pie chart |
| **Reports** | Export to PDF or Excel |
| **Privacy** | 100 % local — no data leaves your machine |

---

## Requirements

- Windows 10 / 11 (64-bit)
- [Ollama](https://ollama.com) *(optional — for AI features)*

---

## Installation

### Option A — Windows Installer (recommended)

1. Download `FinanceManagerSetup.exe` from the releases page.
2. Run the installer and follow the prompts.
3. Launch **Personal Finance Manager** from the Start Menu.

### Option B — Run from source

```bash
# Clone the repository
git clone https://github.com/yourusername/finance-manager.git
cd finance-manager/finance_manager

# Install dependencies (Python 3.10+)
pip install -e ".[dev]"
# or with uv:
uv sync --all-groups

# Run the application
python -m finance_manager
```

---

## First Run

On first launch the setup wizard asks for your preferred currency symbol. You can change this later in **Edit → Preferences**.

---

## Importing Statements

1. Click **File → Import Statement** (or press `Ctrl+I`).
2. Select a PDF, CSV, XLSX, or DOCX bank statement.
3. Review the parsed transactions — correct categories if needed.
4. Click **Import** to save them.

Supported formats:

- **PDF** — pdfplumber table extraction
- **CSV** — auto-detects Date / Description / Amount columns
- **XLSX / XLS** — openpyxl-based parsing
- **DOCX** — python-docx text extraction

---

## AI Categorisation (Ollama)

1. Install [Ollama](https://ollama.com/download).
2. Pull a model: `ollama pull llama3.2:3b`
3. Start Ollama: `ollama serve`
4. In Finance Manager go to **Edit → Preferences → AI / Ollama** and confirm the host / model.

When Ollama is running, imported transactions are categorised automatically. Suggestions below the confidence threshold are shown for manual review.

---

## Settings

Open **Edit → Preferences** to configure:

- **General** — currency symbol, date display format
- **AI / Ollama** — host URL, model, enable/disable, confidence threshold
- **Database** — automatic backups (copies kept, interval in days)

---

## Building from Source

### Prerequisites

```bash
pip install pyinstaller
# or: uv sync --all-groups
```

### Build executable

```bash
cd finance_manager
python build.py --clean
# Output: dist/FinanceManager.exe
```

### Create Windows installer

1. Install [Inno Setup 6](https://jrsoftware.org/isdl.php).
2. Open `installer.iss` in the Inno Setup IDE and click **Build → Compile**.
3. Output: `dist/FinanceManagerSetup.exe`

---

## Development

```bash
# Run unit tests
uv run pytest tests/unit/ -v

# Run integration tests
uv run pytest tests/integration/ -v

# Run all tests
uv run pytest tests/ -v

# Lint / format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy src/finance_manager --ignore-missing-imports
```

---

## Project Structure

```
finance_manager/
├── src/finance_manager/
│   ├── ai/            # Ollama client, categoriser, insight generator
│   ├── core/          # Config, constants, errors, logging
│   ├── database/      # SQLite connection, migrations, schema
│   ├── importers/     # PDF, CSV, XLSX, DOCX importers
│   ├── models/        # Domain models (Account, Transaction, Budget …)
│   ├── repositories/  # Data access layer
│   ├── services/      # Business logic
│   └── ui/            # PyQt6 views, dialogs, widgets
├── tests/
│   ├── unit/          # Fast tests — models, services, utils, UI
│   └── integration/   # File I/O and AI tests
├── build.py           # Build automation
├── installer.iss      # Inno Setup installer script
└── main.spec          # PyInstaller spec
```

---

## License

MIT
