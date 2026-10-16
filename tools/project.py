#!/usr/bin/env python3
"""Maintain the independent Light/Dark packages from the unified repository."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("light", "dark")
EXCLUDED = {".git", "dist", "__pycache__"}


def update_manifest(package):
    """Accept intentional source edits by updating hashes, without changing versions."""
    target = package / "manifest.json"
    manifest = json.loads(target.read_text())
    hashes = {}
    for source in sorted(package.rglob("*")):
        relative = source.relative_to(package)
        if (not source.is_file() or source == target or
                any(part in EXCLUDED for part in relative.parts) or source.suffix == ".pyc"):
            continue
        hashes[relative.as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest["sha256"] = hashes
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"{package.name}: {len(hashes)} hashes atualizados; versão {manifest['version']}.", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "test", "build", "manifest"))
    parser.add_argument("--variant", choices=("all",) + VARIANTS, default="all")
    args = parser.parse_args(argv)
    variants = VARIANTS if args.variant == "all" else (args.variant,)
    commands = {
        "check": [sys.executable, "-c", "import install; m=install.verify_assets(); print('Integridade OK; versão', m['version'])"],
        "test": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        "build": [sys.executable, "build.py"],
    }
    for variant in variants:
        package = ROOT / variant
        print(f"{args.action}: {variant}", flush=True)
        if args.action == "manifest":
            update_manifest(package)
        else:
            # Separate processes keep identically named package modules isolated.
            subprocess.run(commands[args.action], cwd=package, check=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        sys.exit(1)
