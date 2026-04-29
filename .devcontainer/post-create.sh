#!/bin/bash
# Runs once, the first time the container is built.
# Sets up the Python venv and git defaults inside the container.

set -e

echo "==> Setting up Python virtual environment at /workspace/.venv"
python -m venv /workspace/.venv
source /workspace/.venv/bin/activate
pip install --upgrade pip

# If requirements.txt exists, install. If not, Claude will create it.
if [ -f /workspace/requirements.txt ]; then
  echo "==> Installing dependencies from requirements.txt"
  pip install -r /workspace/requirements.txt
fi

echo "==> Configuring git defaults"
git config --global init.defaultBranch main
git config --global pull.rebase false

echo ""
echo "============================================================"
echo "Container ready."
echo ""
echo "One-time setup steps to run yourself:"
echo "  1. gh auth login                   (authenticate to GitHub)"
echo "  2. git config --global user.name \"Your Name\""
echo "  3. git config --global user.email \"you@example.com\""
echo ""
echo "Then start Claude Code with:"
echo "  claude --dangerously-skip-permissions"
echo "============================================================"