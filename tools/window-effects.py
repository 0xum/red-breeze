#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Apply or restore the Papirus Breeze Wayland window effects."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

GLASS = 'glass'
CORNERS = 'kwin4_effect_shapecorners'
EFFECTS = ('blur', GLASS, CORNERS)
CLASSES = ('org.kde.dolphin', 'org.kde.konsole')
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


def profile():
    groups = {
        'Plugins': {'blurEnabled': 'false', 'glassEnabled': 'true', CORNERS + 'Enabled': 'true'},
        'Effect-blurplus': {
            'WindowClasses': '\n'.join((*CLASSES, 'plasmashell', 'org.kde.plasmashell')),
            'DecorWindowClasses': '\n'.join(CLASSES),
            'BlurMatching': 'true', 'BlurNonMatching': 'false', 'BlurDecorations': 'false',
            'IgnoreContentBlurRegion': 'false', 'UseDeclaredCornerRadius': 'true',
        },
        'Round-Corners': {
            'Size': '11', 'InactiveCornerRadius': '11', 'UseSquircleShape': 'true',
            'Squircleness': '0.55', 'UseNativeDecorationShadows': 'true',
            'DisableRoundMaximize': 'true', 'DisableRoundFullScreen': 'true',
            'DisableRoundTile': 'false', 'Exclusions': 'dolphin,konsole',
            **{prefix + 'OutlineThickness': '0' for prefix in
               ('', 'Inactive', 'Second', 'InactiveSecond', 'Outer', 'InactiveOuter')},
        },
    }
    for group, settings in groups.items():
        for name, value in settings.items():
            yield ('kwinrc', group, name), value
    order_key = ('kwinrulesrc', 'General', 'Order')
    order = setting('kreadconfig6', order_key)
    for window_class in CLASSES:
        group = 'papirus-breeze-' + window_class
        for name, value in {
            'Description': f'Papirus Breeze opacity ({window_class})',
            'wmclass': window_class, 'wmclassmatch': '1',
            'opacityactive': '90', 'opacityactiverule': '2',
            'opacityinactive': '90', 'opacityinactiverule': '2',
        }.items():
            yield ('kwinrulesrc', group, name), value
    ids = ['papirus-breeze-' + name for name in CLASSES]
    yield order_key, ','.join(dict.fromkeys(ids + [item for item in order.split(',') if item]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'restore'))
    args = parser.parse_args()
    if os.geteuid() == 0 or os.environ.get('XDG_SESSION_TYPE') != 'wayland':
        raise RuntimeError('Run as your normal user in the Plasma Wayland session.')
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state')))
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
    values = list(profile())
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
