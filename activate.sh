#!/bin/bash
# Activate virtual environment on Unix-like systems
if [ -f "venv/bin/activate" ]; then
  # macOS/Linux
  . venv/bin/activate
else
  echo "venv not found. Create it with: python -m venv venv" >&2
  exit 1
fi
