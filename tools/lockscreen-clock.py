#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Disable the Plasma desktop lock screen's clock and date shadow."""
import argparse
import os
from pathlib import Path
import shutil
import tempfile

SOURCE = Path('/usr/share/plasma/shells/org.kde.plasma.desktop/contents/lockscreen/LockScreenUi.qml')
BACKUP = Path('/var/lib/papirus-breeze-login/LockScreenUi.qml.before')
ORIGINAL = ('id: clockShadow\n'
            '            anchors.fill: clock\n'
            '            source: clock\n'
            '            visible: !lockScreenUi.softwareRendering && config.alwaysShowClock')
UPDATED = ORIGINAL.rsplit('visible:', 1)[0] + 'visible: false'


def rewrite(source, old, new):
    if source.count(old) != 1:
        raise SystemExit('Unrecognized clock shadow QML. No files changed.')
    return source.replace(old, new, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'restore'))
    args = parser.parse_args()
    source = SOURCE.read_text()
    old, new = (ORIGINAL, UPDATED) if args.action == 'apply' else (UPDATED, ORIGINAL)
    if source.count(new) == 1 and old not in source:
        print('Clock shadow is already configured.')
        return
    updated = rewrite(source, old, new)
    if os.geteuid() != 0:
        raise SystemExit('Run with sudo or pkexec.')
    if args.action == 'apply':
        BACKUP.parent.mkdir(parents=True, exist_ok=True)
        if not BACKUP.exists():
            shutil.copy2(SOURCE, BACKUP)
    with tempfile.NamedTemporaryFile(mode='w', dir=SOURCE.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(updated)
            file.flush()
            shutil.copystat(SOURCE, temporary)
            temporary.replace(SOURCE)
        finally:
            temporary.unlink(missing_ok=True)
    print('Lock screen clock shadow updated. The change takes effect on the next lock.')


if __name__ == '__main__':
    main()
