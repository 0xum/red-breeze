#!/usr/bin/env python3
"""Maintain the independent Light/Dark packages from the unified repository."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

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
    print(f"{package.name}: {len(hashes)} hashes updated; version {manifest['version']}.", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "test", "build", "manifest"))
    parser.add_argument("--variant", choices=("all",) + VARIANTS, default="all")
    args = parser.parse_args(argv)
    variants = VARIANTS if args.variant == "all" else (args.variant,)
    commands = {
        "check": [sys.executable, "-c", "import install; m=install.verify_assets(); print('Integrity OK; version', m['version'])"],
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
    if args.variant == 'all' and args.action == 'test':
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True)
    if args.variant == 'all' and args.action == 'build':
        versions = {json.loads((ROOT / v / 'manifest.json').read_text())['version'] for v in VARIANTS}
        if len(versions) != 1:
            raise ValueError('Both variants must have the same version for the complete archive.')
        name = 'papirus-breeze-' + versions.pop()
        archive = ROOT / 'dist' / (name + '.tar.gz')
        archive.parent.mkdir(exist_ok=True)
        with tarfile.open(archive, 'w:gz', format=tarfile.PAX_FORMAT) as tar:
            for entry in ('install.py', 'README.md', 'README.pt-BR.md', 'CHANGELOG.md', 'LICENSE', 'THIRD_PARTY.md', 'docs', 'tools', 'tests', *VARIANTS):
                source = ROOT / entry
                for path in ([source] if source.is_file() else sorted(source.rglob('*'))):
                    relative = path.relative_to(ROOT)
                    if path.is_file() and not any(p in EXCLUDED for p in relative.parts) and path.suffix != '.pyc':
                        tar.add(path, arcname=name + '/' + str(relative), recursive=False)
        print(archive)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
