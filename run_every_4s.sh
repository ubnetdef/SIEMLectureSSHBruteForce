#!/bin/bash
# Runs ssh_run.py on a sweep, every 4 seconds, until Ctrl+C.
# Usage: ./run_every_4s.sh -x 0-36 -u sysadmin -c "whoami"
# Any arguments are passed straight through to ssh_run.py.

while true; do
    python3 ssh_run.py --once "$@"
    sleep 4
done
