#!/usr/bin/env python3
"""Run a command over SSH on a set of hosts.

Usage:
    python ssh_run.py -H hosts.txt -u user -c "uname -a"
    python ssh_run.py -H 10.0.0.5 10.0.0.6 -u user -k ~/.ssh/id_ed25519 -c "uptime"

hosts.txt: one host per line (optionally host:port); blank lines and # comments ignored.
Requires: pip install paramiko
"""
import argparse
import getpass
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import paramiko


DEFAULT_RANGE = "0-36"


def hosts_from_range(spec):
    """'0-36' -> 10.42.0.7 ... 10.42.36.7"""
    lo, _, hi = spec.partition("-")
    return [f"10.42.{x}.7" for x in range(int(lo), int(hi or lo) + 1)]


def load_hosts(items):
    hosts = []
    for item in items:
        if os.path.isfile(item):
            with open(item) as f:
                hosts += [l.strip() for l in f if l.strip() and not l.startswith("#")]
        else:
            hosts.append(item)
    return hosts


def run_on_host(host, user, password, key_file, command, timeout):
    name, _, port = host.partition(":")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # lab use: accept unknown host keys
    try:
        client.connect(
            name,
            port=int(port) if port else 22,
            username=user,
            password=password,
            key_filename=key_file,
            timeout=timeout,
            look_for_keys=key_file is None and password is None,
        )
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        out, err = stdout.read().decode(), stderr.read().decode()
        code = stdout.channel.recv_exit_status()
        return host, code, out, err
    except Exception as e:
        return host, -1, "", f"{type(e).__name__}: {e}"
    finally:
        client.close()


def main():
    p = argparse.ArgumentParser(description="Run a command on multiple hosts via SSH")
    p.add_argument("-x", "--range", default=DEFAULT_RANGE,
                   help="x range for 10.42.x.7 (default: 0-36)")
    p.add_argument("-H", "--hosts", nargs="+", help="hosts and/or host files (overrides -x)")
    p.add_argument("-u", "--user", required=True)
    p.add_argument("-k", "--key", help="private key file")
    p.add_argument("-c", "--command", required=True)
    p.add_argument("-t", "--timeout", type=int, default=3, help="per-host timeout in seconds (default 3)")
    p.add_argument("-w", "--workers", type=int, default=0, help="parallel workers (default: one per host)")
    p.add_argument("-i", "--interval", type=float, default=5, help="seconds between sweeps (default 5)")
    p.add_argument("--once", action="store_true", help="run a single sweep and exit")
    a = p.parse_args()

    # Password auth is the default; it is prompted once and reused for every host.
    # Set SSH_PASSWORD to skip the prompt. Passing -k switches to key auth instead.
    password = None
    if not a.key:
        password = os.environ.get("SSH_PASSWORD") or getpass.getpass("SSH password: ")
    hosts = load_hosts(a.hosts) if a.hosts else hosts_from_range(a.range)

    try:
        while True:
            start = time.monotonic()
            print(f"--- sweep at {time.strftime('%H:%M:%S')} ---")
            with ThreadPoolExecutor(max_workers=a.workers or len(hosts)) as pool:
                futures = [pool.submit(run_on_host, h, a.user, password, a.key, a.command, a.timeout) for h in hosts]
                for fut in as_completed(futures):
                    host, code, out, err = fut.result()
                    print(f"=== {host} (exit {code}) ===")
                    if out:
                        print(out.rstrip())
                    if err:
                        print(f"[stderr] {err.rstrip()}")
            if a.once:
                break
            time.sleep(max(0, a.interval - (time.monotonic() - start)))
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
