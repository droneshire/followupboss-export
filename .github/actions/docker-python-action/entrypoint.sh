#!/bin/bash
set -e

echo "Entrypoint version: $1"

pip install --upgrade --break-system-packages pip pip-tools uv
uv pip compile --strip-extras --output-file=requirements.txt packages/requirements.in
uv pip install --system --break-system-packages -r requirements.txt

# Lint with black
make check_format PYTHON=python3

# Lint with mypy
make mypy PYTHON=python3

# Lint with pylint
make pylint PYTHON=python3

# If you need to keep the container running (for services etc.), uncomment the next line
# tail -f /dev/null
RESULT="🍻🍻🍻 Passed!"

if [[ -n "$GITHUB_OUTPUT" ]]; then
    echo "result=$RESULT" >> "$GITHUB_OUTPUT"
fi
