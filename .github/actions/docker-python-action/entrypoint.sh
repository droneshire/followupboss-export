#!/bin/bash
set -e

echo "Entrypoint version: $1"

pip install --upgrade --break-system-packages pip pip-tools uv
uv pip compile --strip-extras --output-file=requirements.txt packages/base_requirements.in packages/dev_requirements.in
uv pip install --system --break-system-packages -r requirements.txt

# Install dependencies
make types_build

# Lint with black
make check_format PYTHON=python3

# Lint with mypy
make mypy PYTHON=python3

# Lint with pylint
make pylint PYTHON=python3

# Start the Redis server
redis-server --daemonize yes

# Set the data directory for PostgreSQL
DATA_DIR="/var/lib/postgresql/data"

# Check if the data directory exists and is empty
if [ ! -d "$DATA_DIR" ] || [ -z "$(ls -A $DATA_DIR)" ]; then
  echo "Initializing PostgreSQL data directory..."
  gosu postgres initdb -D "$DATA_DIR"
fi

gosu postgres postgres -D "$DATA_DIR" &

# Wait for PostgreSQL server to be up
timeout 10 bash -c '
until pg_isready -h localhost -p 5432 -U postgres
do
    echo "Waiting for PostgreSQL server to be up..."
    sleep 1
done
'

# Test with pytest
make test PYTHON=python3

# If you need to keep the container running (for services etc.), uncomment the next line
# tail -f /dev/null
RESULT="🍻🍻🍻 Passed!"

if [[ -n "$GITHUB_OUTPUT" ]]; then
    echo "result=$RESULT" >> "$GITHUB_OUTPUT"
fi

# if there's a .coverage file, echo the result of the coverage report to the output
if [[ -f .coverage ]]; then
    COVERAGE_REPORT=$(coverage report)
    echo $(coverage report)
    # get the percentage from the coverage report
    COVERAGE_PERCENT=$(echo $COVERAGE_REPORT | grep -oP 'TOTAL.*\d+\%' | grep -oP '\d+\%')
    echo "coverage_percentage=$COVERAGE_PERCENT" >> "$GITHUB_OUTPUT"
fi
