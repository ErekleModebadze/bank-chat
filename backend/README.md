# Quick Start

1. Install uv [DOCUMENTATION](https://docs.astral.sh/uv/getting-started/installation/)
```bash
#On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Install via pip
pip install uv

# Alternative: Install via pipx
pipx install uv
```

1. Create virtual environment:

```bash
# Create a virtual environment
uv venv --python 3.12
```

2. Activate a virtual environment

```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

2. Install project dependencies using uv:

```bash
uv pip install -e .
```



