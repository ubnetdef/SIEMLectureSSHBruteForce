# ssh_run

Runs a command over SSH on a set of hosts, repeating every 5 seconds.

By default it targets `10.42.0.7` through `10.42.36.7` (x = 0-36).

## Setup

```
pip install paramiko
```

## Usage

```
python ssh_run.py -x 0-36 -u myuser -k ~/.ssh/id_ed25519 -c "hostname"
```

| Flag | Meaning |
|------|---------|
| `-u` | SSH username (required) |
| `-c` | Command to run (required) |
| `-k` | Private key file |
| `-p` | Prompt for a password |
| `-x` | Range for x in `10.42.x.7` (default `0-36`) |
| `-H` | Hosts or host file (overrides `-x`) |
| `-i` | Seconds between sweeps (default 5) |
| `--once` | Run one sweep and exit |
| `-t` | Per-host timeout in seconds (default 10) |
| `-w` | Parallel workers (default 5) |

Press Ctrl+C to stop.

## Note

Unknown host keys are rejected by default. For a lab, change `RejectPolicy` to `AutoAddPolicy` in `run_on_host`.
