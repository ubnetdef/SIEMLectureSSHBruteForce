# ssh_run

Runs a command over SSH on a set of hosts, repeating every 5 seconds.

By default it targets `10.42.0.7` through `10.42.36.7` (x = 0-36).

## Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Debian/Ubuntu you may first need `apt install python3-venv`. Alternatively, `apt install python3-paramiko` works without a venv.

## Usage

```
python ssh_run.py -x 0-36 -u myuser -c "hostname"
```

You'll be prompted for the password once; it's used for every host. To skip the prompt, set `SSH_PASSWORD` in the environment.

| Flag | Meaning |
|------|---------|
| `-u` | SSH username (required) |
| `-c` | Command to run (required) |
| `-k` | Private key file (optional; uses key auth instead of a password) |
| `-x` | Range for x in `10.42.x.7` (default `0-36`) |
| `-H` | Hosts or host file (overrides `-x`) |
| `-i` | Seconds between sweeps (default 5) |
| `--once` | Run one sweep and exit |
| `-t` | Per-host timeout in seconds (default 3) |
| `-w` | Parallel workers (default: one per host, so all hosts run at once) |

Press Ctrl+C to stop.

## Note

Unknown host keys are accepted automatically (lab use). To be strict, change `AutoAddPolicy` to `RejectPolicy` in `run_on_host`.
