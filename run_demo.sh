#!/usr/bin/env bash

set -euo pipefail

echo "Starting AutoStream Social-to-Lead demo..."

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment (.venv)"
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies from requirements.txt"
pip install -r requirements.txt

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo ""
  echo "OPENAI_API_KEY is not set."
  echo "The agent will still run using local retrieval fallback responses."
  echo "To use GPT-4o-mini responses, run:"
  echo "export OPENAI_API_KEY=\"your_key_here\""
  echo ""
fi

echo "Launching agent..."
python agent.py
