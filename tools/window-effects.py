#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Apply or restore the Papirus Breeze Wayland window effects."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile

GLASS = 'glass'
CORNERS = 'kwin4_effect_shapecorners'
EFFECTS = ('blur', GLASS, CORNERS)
CLASSES = ('org.kde.dolphin', 'org.kde.konsole')
CHATGPT_CLASS = 'Chatgpt'
MISSING = '__papirus_breeze_missing__'


def command(*args):
    return subprocess.check_output(args, text=True).rstrip('\n')


def effect(method, name):
    return command('qdbus6', 'org.kde.KWin', '/Effects', method, name)


def setting(tool, key, *args):
    filename, group, name = key
    return command(tool, '--file', filename, '--group', group, '--key', name, *args)


def restore(values, loaded):
    for name in EFFECTS:
        effect('unloadEffect', name)
    for key, value in values:
        setting('kwriteconfig6', key, '--delete' if value == MISSING else value)
    command('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
    for name in EFFECTS:
        if name not in loaded:
            effect('unloadEffect', name)
    for name in loaded:
        if effect('isEffectLoaded', name) != 'true' and effect('loadEffect', name) != 'true':
            raise RuntimeError(f'Could not restore {name}.')


def profile(include_chatgpt=False):
    classes = (*CLASSES, CHATGPT_CLASS) if include_chatgpt else CLASSES
    exclusions = 'dolphin,konsole' if include_chatgpt else 'dolphin,konsole,chatgpt'
    groups = {
        'Plugins': {'blurEnabled': 'false', 'glassEnabled': 'true', CORNERS + 'Enabled': 'true'},
        'Effect-blurplus': {
            'WindowClasses': '\n'.join((*classes, 'plasmashell', 'org.kde.plasmashell')),
            'DecorWindowClasses': '\n'.join(classes),
            'BlurMatching': 'true', 'BlurNonMatching': 'false', 'BlurDecorations': 'false',
            'IgnoreContentBlurRegion': 'false', 'UseDeclaredCornerRadius': 'true',
        },
        'Round-Corners': {
            'Size': '11', 'InactiveCornerRadius': '11', 'UseSquircleShape': 'true',
            'Squircleness': '0.55', 'UseNativeDecorationShadows': 'true',
            'DisableRoundMaximize': 'true', 'DisableRoundFullScreen': 'true',
            'DisableRoundTile': 'false', 'Exclusions': exclusions,
            **{prefix + 'OutlineThickness': '0' for prefix in
               ('', 'Inactive', 'Second', 'InactiveSecond', 'Outer', 'InactiveOuter')},
        },
    }
    for group, settings in groups.items():
        for name, value in settings.items():
            yield ('kwinrc', group, name), value
    order_key = ('kwinrulesrc', 'General', 'Order')
    order = setting('kreadconfig6', order_key)
    ids = []
    for window_class in classes:
        group = 'papirus-breeze-' + window_class.lower()
        ids.append(group)
        for name, value in {
            'Description': f'Papirus Breeze opacity ({window_class})',
            'wmclass': window_class, 'wmclassmatch': '1',
            'opacityactive': '90', 'opacityactiverule': '2',
            'opacityinactive': '90', 'opacityinactiverule': '2',
        }.items():
            yield ('kwinrulesrc', group, name), value
    yield order_key, ','.join(dict.fromkeys(ids + [item for item in order.split(',') if item]))


def prepare_upgrade(state):
    """Disable and remove local plugins before upgrading KWin, keeping recovery data."""
    installed = set(command('pacman', '-Qq').splitlines())
    packages = [name for name in ('kwin-effect-rounded-corners', 'kwin-effects-glass-local')
                if name in installed]
    if not packages:
        print('No local KWin effect packages to remove. Run sudo pacman -Syu.')
        return
    # Authenticate before changing the session. Never collect passwords in Python.
    subprocess.run(['sudo', '-v'], check=True)
    directory = state / 'papirus-breeze'
    directory.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='kwin-upgrade-', dir=directory))
    config = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    for name in ('kwinrc', 'kwinrulesrc'):
        if (config / name).exists():
            shutil.copy2(config / name, backup / name)
    managed = directory / 'window-effects.json'
    if managed.exists():
        shutil.copy2(managed, backup / managed.name)
    (backup / 'packages.txt').write_text(command('pacman', '-Q', *packages) + '\n')
    print(f'Recovery data: {backup}', flush=True)
    for name in (GLASS, CORNERS):
        setting('kwriteconfig6', ('kwinrc', 'Plugins', name + 'Enabled'), 'false')
        effect('unloadEffect', name)
    setting('kwriteconfig6', ('kwinrc', 'Plugins', 'blurEnabled'), 'true')
    command('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
    if effect('isEffectLoaded', 'blur') != 'true' and effect('loadEffect', 'blur') != 'true':
        raise RuntimeError('Could not enable the built-in blur; packages were not removed.')
    # Keep dependency checks and pacman's own confirmation. Do not remove dependencies.
    subprocess.run(['sudo', 'pacman', '-R', *packages], check=True)
    print('Local effects removed. Run sudo pacman -Syu, then log out and back in. '
          'Rebuild both plugins for the installed KWin before enabling them again.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'restore', 'prepare-upgrade'))
    parser.add_argument('--chatgpt', action='store_true',
                        help='include the ChatGPT desktop window in the effects profile (apply only)')
    args = parser.parse_args()
    if args.chatgpt and args.action != 'apply':
        parser.error('--chatgpt requires apply')
    if os.geteuid() == 0 or os.environ.get('XDG_SESSION_TYPE') != 'wayland':
        raise RuntimeError('Run as your normal user in the Plasma Wayland session.')
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state')))
    if args.action == 'prepare-upgrade':
        prepare_upgrade(state)
        return
    backup = state / 'papirus-breeze/window-effects.json'
    if args.action == 'restore':
        saved = json.loads(backup.read_text())
        restore(saved['values'], saved['loaded'])
        backup.unlink()
        print('Previous window effects restored.')
        return
    if backup.exists():
        raise RuntimeError('The profile is already managed. Restore it before applying again.')
    for name in (GLASS, CORNERS):
        if effect('isEffectSupported', name) != 'true':
            raise RuntimeError(f'Install a compatible {name} plugin first.')
    values = list(profile(include_chatgpt=args.chatgpt))
    saved = {
        'values': [(key, setting('kreadconfig6', key, '--default', MISSING)) for key, _ in values],
        'loaded': [name for name in EFFECTS if effect('isEffectLoaded', name) == 'true'],
    }
    backup.parent.mkdir(parents=True, exist_ok=True)
    with backup.open('x') as file:
        json.dump(saved, file, indent=2)
    try:
        for name in EFFECTS:
            effect('unloadEffect', name)
        for key, value in values:
            setting('kwriteconfig6', key, value)
        command('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
        for name in (GLASS, CORNERS):
            if effect('isEffectLoaded', name) != 'true' and effect('loadEffect', name) != 'true':
                raise RuntimeError(f'Could not load {name}.')
    except Exception:
        restore(saved['values'], saved['loaded'])
        backup.unlink()
        raise
    print(f'Window effects applied. Restore data: {backup}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
