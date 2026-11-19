#!/usr/bin/env python3
"""Build/install the version-specific Papirus Breeze native internal-corner effect."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

EFFECT = 'papirus_inner_corners'
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/kwin/papirus-inner-corners'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def running_version():
    info = subprocess.check_output(['qdbus6', 'org.kde.KWin', '/KWin', 'supportInformation'], text=True)
    match = re.search(r'^KWin version: (\d+\.\d+\.\d+)', info, re.MULTILINE)
    if not match:
        raise RuntimeError('Could not identify the running KWin version.')
    return match[1]


def plugin_directory():
    candidates = [shutil.which('qtpaths6'), shutil.which('qtpaths'), '/usr/lib/qt6/bin/qtpaths6']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(subprocess.check_output([candidate, '--plugin-dir'], text=True).strip())
    raise RuntimeError('Qt 6 qtpaths is required to locate the native plugin directory.')


def install(state, target, version, cmake, extra=()):
    record_file = state / 'native-inner-corners.json'
    old = json.loads(record_file.read_text()) if record_file.exists() else None
    source_hash = hashlib.sha256(b''.join(p.name.encode() + p.read_bytes()
                                for p in sorted(SOURCE.iterdir()) if p.is_file() and p.name != "README.md")).hexdigest()
    if (old and old['kwin'] == version and old['target'] == str(target)
            and old['source'] == source_hash and digest(target) == old['sha256']):
        print('Native internal corners already match KWin ' + version + '.')
        return
    if old and old['target'] != str(target):
        raise RuntimeError('The recorded plugin directory differs; restore the old installation first.')
    if old and target.exists() and digest(target) != old['sha256']:
        raise RuntimeError('The installed plugin was modified; preserving it instead of overwriting it.')
    if not cmake or not shutil.which(cmake):
        raise RuntimeError('CMake and the matching KWin/Qt development files are required. '
                           'Set CMAKE or pass --cmake; see docs/WINDOW_DECORATIONS.md.')
    state.mkdir(parents=True, exist_ok=True)
    build = state / ('build-' + version)
    subprocess.run([cmake, '-S', str(SOURCE), '-B', str(build), '-G', 'Ninja',
                    '-DCMAKE_BUILD_TYPE=Release', *extra], check=True)
    subprocess.run([cmake, '--build', str(build), '--parallel', '2'], check=True)
    binary = build / ('plugins/kwin/effects/plugins/' + EFFECT + '.so')
    if not binary.is_file():
        raise RuntimeError('The build did not produce the expected plugin.')
    previous = old.get('previous') if old else None
    if not old and target.exists():
        previous = str(state / 'previous-plugin.so')
        shutil.copy2(target, previous)
    # Do not replace an in-use shared object. KDE may cache it until session restart.
    was_loaded = subprocess.check_output(['qdbus6', 'org.kde.KWin', '/Effects',
                                          'isEffectLoaded', EFFECT], text=True).strip() == 'true'
    subprocess.run(['qdbus6', 'org.kde.KWin', '/Effects', 'unloadEffect', EFFECT], check=True)
    try:
        subprocess.run(['pkexec', '/usr/bin/install', '-m', '0755', str(binary), str(target)], check=True)
    finally:
        if was_loaded:
            subprocess.run(['qdbus6', 'org.kde.KWin', '/Effects', 'loadEffect', EFFECT], check=True)
    record = {'kwin': version, 'source': source_hash, 'target': str(target),
              'sha256': digest(target), 'previous': previous}
    record_file.write_text(json.dumps(record, indent=2) + '\n')
    print('Native internal corners installed for KWin ' + version + '.')
    print('After updating an already loaded binary, log out and back in to clear KDE library caches.')


def remove(state):
    record_file = state / 'native-inner-corners.json'
    record = json.loads(record_file.read_text())
    target = Path(record['target'])
    if digest(target) != record['sha256']:
        raise RuntimeError('The installed plugin was modified; preserving it and its recovery record.')
    subprocess.run(['qdbus6', 'org.kde.KWin', '/Effects', 'unloadEffect', EFFECT], check=True)
    if record['previous']:
        subprocess.run(['pkexec', '/usr/bin/install', '-m', '0755', record['previous'], str(target)], check=True)
    else:
        subprocess.run(['pkexec', '/usr/bin/rm', str(target)], check=True)
    subprocess.run(['kwriteconfig6', '--file', 'kwinrc', '--group', 'Plugins',
                    '--key', EFFECT + 'Enabled', 'false'], check=True)
    record_file.unlink()
    print('Native plugin removed/restored. Theme assets and unrelated effects were preserved.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'remove'))
    parser.add_argument('--state-dir', type=Path, default=Path(os.environ.get(
        'XDG_STATE_HOME', str(Path.home() / '.local/state'))))
    parser.add_argument('--cmake', default=os.environ.get('CMAKE', 'cmake'))
    parser.add_argument('--cmake-arg', action='append', default=[])
    args = parser.parse_args(argv)
    if os.geteuid() == 0:
        raise RuntimeError('Run as your normal user; Polkit handles native binary installation.')
    state = args.state_dir.expanduser().resolve() / 'papirus-breeze/inner-corners'
    if args.action == 'remove':
        remove(state)
    else:
        target = plugin_directory() / ('kwin/effects/plugins/' + EFFECT + '.so')
        install(state, target, running_version(), args.cmake, args.cmake_arg)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        sys.exit(1)
