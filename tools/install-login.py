#!/usr/bin/env python3
"""Install both login profiles and follow a selected user's Light/Dark theme."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--follow-user', required=True)
    parser.add_argument('--manager', choices=('auto', 'plasma-login', 'sddm'), default='auto')
    parser.add_argument('--source', type=Path, help="explicit path to the selected user's kdeglobals (for XDG_CONFIG_HOME)")
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    for variant in ('light', 'dark'):
        command = [sys.executable, str(ROOT / variant / 'install-login.py'),
                   '--follow-user', args.follow_user, '--manager', args.manager]
        if args.dry_run:
            command.append('--dry-run')
        if args.source:
            command += ['--source', str(args.source)]
        subprocess.run(command, check=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
