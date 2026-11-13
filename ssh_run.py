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
from concurrent.futures import ThreadPoolExecutor

import paramiko


DEFAULT_HOSTS = [f"10.42.{x}.7" for x in range(1, 37)]


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
    client.set_missing_host_key_policy(paramiko.RejectPolicy())  # change to AutoAddPolicy for lab use
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
    p.add_argument("-H", "--hosts", nargs="+", default=DEFAULT_HOSTS,
                   help="hosts and/or host files (default: 10.42.1-36.7)")
    p.add_argument("-u", "--user", required=True)
    p.add_argument("-k", "--key", help="private key file")
    p.add_argument("-p", "--password", action="store_true", help="prompt for a password")
    p.add_argument("-c", "--command", required=True)
    p.add_argument("-t", "--timeout", type=int, default=10)
    p.add_argument("-w", "--workers", type=int, default=5)
    p.add_argument("-i", "--interval", type=float, default=5, help="seconds between sweeps (default 5)")
    p.add_argument("--once", action="store_true", help="run a single sweep and exit")
    a = p.parse_args()

    password = getpass.getpass("SSH password: ") if a.password else None
    hosts = load_hosts(a.hosts)

    try:
        while True:
            start = time.monotonic()
            print(f"--- sweep at {time.strftime('%H:%M:%S')} ---")
            with ThreadPoolExecutor(max_workers=a.workers) as pool:
                futures = [pool.submit(run_on_host, h, a.user, password, a.key, a.command, a.timeout) for h in hosts]
                for fut in futures:
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
