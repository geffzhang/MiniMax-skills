#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_GUIDANCE = (
    "Install OfficeCLI and ensure it is on PATH, or set OFFICECLI_COMMAND "
    "to the absolute path of the officecli executable."
)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def configured_command():
    configured = os.getenv("OFFICECLI_COMMAND", "").strip()
    if configured:
        return configured, "OFFICECLI_COMMAND"
    return "officecli", "PATH"


def resolve_command(command, source):
    if os.path.isabs(command) or os.sep in command or (os.altsep and os.altsep in command):
        if os.path.exists(command):
            return command
        windows_exe = f"{command}.exe"
        if os.name == "nt" and not command.lower().endswith(".exe") and os.path.exists(windows_exe):
            return windows_exe
        return None
    resolved = shutil.which(command)
    if resolved:
        return resolved
    if source == "OFFICECLI_COMMAND":
        return None
    return None


def read_version(executable):
    attempts = ([executable, "--version"], [executable, "version"])
    last_error = ""
    for args in attempts:
        completed = subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        combined = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        if completed.returncode == 0 and combined:
            return combined.splitlines()[0]
        last_error = combined or f"exit code {completed.returncode}"
    raise RuntimeError(last_error or "version command produced no output")


def build_status():
    command, source = configured_command()
    resolved = resolve_command(command, source)
    base = {
        "checkedAt": utc_now(),
        "command": command,
        "resolvedCommand": resolved,
        "source": source,
        "guidance": DEFAULT_GUIDANCE,
    }

    if not resolved:
        base.update(
            {
                "available": False,
                "version": None,
                "reason": f"command not found: {command}",
            }
        )
        return base

    try:
        version = read_version(resolved)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        base.update(
            {
                "available": False,
                "version": None,
                "reason": f"version check failed: {exc}",
            }
        )
        return base

    base.update(
        {
            "available": True,
            "version": version,
            "reason": "ok",
        }
    )
    return base


def print_text(status):
    if status["available"]:
        print("OfficeCLI: available")
        print(f"Command: {status['command']}")
        print(f"Resolved: {status['resolvedCommand']}")
        print(f"Version: {status['version']}")
    else:
        print("OfficeCLI: unavailable")
        print(f"Command: {status['command']}")
        print(f"Reason: {status['reason']}")
        print(status["guidance"])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check whether OfficeCLI is available for office-expert.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    status = build_status()
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_text(status)
    return 0 if status["available"] else 1


if __name__ == "__main__":
    sys.exit(main())
