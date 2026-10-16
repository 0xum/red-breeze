#!/usr/bin/env python3
"""Install, update, and remove Papirus Breeze Light/Dark on KDE Plasma 6."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
THEMES = {v: 'com.delta.papirus-breeze-' + v for v in ('light', 'dark')}
QUICK = {'DefaultLightLookAndFeel': THEMES['light'], 'DefaultDarkLookAndFeel': THEMES['dark']}
NATIVE = {'DefaultLightLookAndFeel': 'org.kde.breeze.desktop',
          'DefaultDarkLookAndFeel': 'org.kde.breezedark.desktop'}


def load_variant(variant):
    spec = importlib.util.spec_from_file_location('papirus_' + variant, ROOT / variant / 'install.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_key(config, filename, group, key):
    return subprocess.check_output(['kreadconfig6', '--file', str(config / filename),
                                    '--group', group, '--key', key], text=True).strip()


def write_key(config, filename, group, key, value):
    command = ['kwriteconfig6', '--file', str(config / filename)]
    for part in group.split(']['):
        command += ['--group', part]
    command += ['--key', key, '--notify']
    subprocess.run(command + (['--delete'] if value is None else [value]), check=True)


def fingerprint(path):
    """Include names and links so removal preserves edited or additional files."""
    if path.is_symlink():
        return 'link:' + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if path.is_dir():
        digest = hashlib.sha256()
        for item in sorted(path.rglob('*')):
            digest.update(item.relative_to(path).as_posix().encode() + b'\0')
            if item.is_symlink() or item.is_file():
                digest.update(fingerprint(item).encode() + b'\0')
            else:
                digest.update(b'directory\0')
        return digest.hexdigest()
    return None


def safe_target(base, relative):
    relative = Path(relative)
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('Invalid resource path: ' + str(relative))
    target = base / relative
    # Never follow a link out of the user's selected installation directories.
    for parent in [target, *target.parents]:
        if parent == base:
            break
        if parent.is_symlink():
            raise ValueError('Symbolic target refused: ' + str(parent))
    return target


def assets():
    result = {}
    for variant in THEMES:
        module = load_variant(variant)
        module.verify_assets()
        for relative in module.asset_paths():
            source = ROOT / variant / 'assets' / relative
            if relative.as_posix() in result:
                if fingerprint(result[relative.as_posix()]) != fingerprint(source):
                    raise ValueError('Recurso compartilhado divergente: ' + str(relative))
            result[relative.as_posix()] = source
    return result


def check(data, applying=False):
    errors = []
    user_data = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))).expanduser().resolve()
    for variant in THEMES:
        module = load_variant(variant)
        problems = module.dependency_errors(data, applying)
        if data != user_data:
            missing_for_user = set(module.dependency_errors(user_data))
            problems = [p for p in problems if not p.startswith('Missing icon/cursor theme:') or p in missing_for_user]
        errors += problems
    for command in ('kreadconfig6', 'kwriteconfig6'):
        if not shutil.which(command):
            errors.append('Missing command: ' + command)
    if sys.platform != 'linux':
        errors.append('This installer requires Linux with KDE Plasma 6.')
    if shutil.which('plasmashell'):
        version = subprocess.check_output(['plasmashell', '--version'], text=True)
        if not version.strip().split()[-1].startswith('6.'):
            errors.append('KDE Plasma 6 is required: ' + version.strip())
    else:
        errors.append('Missing command: plasmashell (KDE Plasma 6).')
    return sorted(set(errors))


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def install(data, config, state, apply=None, layout=False, dry_run=False):
    sources = assets()
    errors = check(data, applying=bool(apply))
    if errors:
        raise RuntimeError('\n'.join(errors) + '\nSee prerequisites in docs/INSTALLATION.md.')
    record_file = state / 'papirus-breeze/installation.json'
    previous = json.loads(record_file.read_text()) if record_file.exists() else None
    if previous and (previous['data'] != str(data) or previous['config'] != str(config)):
        raise ValueError('This state directory already manages another installation destination.')
    for relative in sources:
        safe_target(data, relative)
    print('Install/update Light and Dark and register both in Quick Settings.')
    if apply:
        print('Apply: ' + apply + ('; replace panels.' if layout else '; preserve panels.'))
    if dry_run:
        print('Dry run: no files changed.')
        return
    module = load_variant('light')
    backup = module.Backup(state, package='papirus-breeze')
    # First registration is retained across upgrades. Legacy self-references return to Breeze.
    defaults = previous['quick_previous'] if previous else {
        key: read_key(config, 'kdeglobals', 'KDE', key) for key in QUICK}
    defaults = {key: NATIVE[key] if value in THEMES.values() else value
                for key, value in defaults.items()}
    backup.save(record_file)
    backup.save(config / 'kdeglobals')
    try:
        for relative, source in sources.items():
            module.copy_asset(source, data / relative, backup)
        for key, value in QUICK.items():
            write_key(config, 'kdeglobals', 'KDE', key, value)
        if apply:
            for name in ('gtkrc', 'gtkrc-2.0', 'gtk-3.0/settings.ini', 'gtk-4.0/settings.ini',
                         'xsettingsd/xsettingsd.conf', 'fish/config.fish', 'fish/papirus-breeze.fish'):
                backup.save(config / name)
            load_variant(apply).apply_profile(data, config, backup, layout)
        atomic_json(record_file, {'schema': 1, 'data': str(data), 'config': str(config),
                                 'quick_previous': defaults,
                                 'assets': {r: fingerprint(data / r) for r in sources}})
    except Exception:
        restore_backup(backup.path)
        raise
    print('Installation complete. Reopen System Settings to refresh Quick Settings.')
    print('Backup: ' + str(backup.path))


def restore_backup(path):
    spec = importlib.util.spec_from_file_location('papirus_restore', ROOT / 'light/restore.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.restore(path)


def cleanup_config(data, config, backup, live):
    """Change only settings that still refer to this package."""
    def replace(filename, group, key, predicate, value):
        current = read_key(config, filename, group, key)
        if predicate(current):
            backup.save(config / filename)
            write_key(config, filename, group, key, value)

    current = read_key(config, 'kdeglobals', 'KDE', 'LookAndFeelPackage')
    scheme = read_key(config, 'kdeglobals', 'General', 'ColorScheme')
    active = current in THEMES.values() or scheme in ('PapirusBreezeLight', 'PapirusBreezeDark')
    dark = current == THEMES['dark'] or scheme == 'PapirusBreezeDark'
    if active:
        native = NATIVE['DefaultDarkLookAndFeel' if dark else 'DefaultLightLookAndFeel']
        if live:
            for name in ('kdeglobals', 'kdedefaults', 'kwinrc', 'plasmarc', 'kcminputrc',
                         'ksplashrc', 'plasma-org.kde.plasma.desktop-appletsrc',
                         'gtkrc', 'gtkrc-2.0', 'gtk-3.0/settings.ini', 'gtk-4.0/settings.ini'):
                backup.save(config / name)
            subprocess.run(['plasma-apply-lookandfeel', '--apply', native], check=True)
        replace('kdeglobals', 'KDE', 'LookAndFeelPackage', lambda v: v in THEMES.values(), native)
    for filename in ('kdeglobals', 'kdedefaults/kdeglobals'):
        replace(filename, 'General', 'ColorScheme', lambda v: v in ('PapirusBreezeLight', 'PapirusBreezeDark'), 'BreezeDark' if dark else 'BreezeLight')
        replace(filename, 'Icons', 'Theme', lambda v: v in ('PapirusBreezeLight', 'PapirusBreezeDark'), 'breeze-dark' if dark else 'breeze')
    replace('plasmarc', 'Theme', 'name', lambda v: v == 'PapirusBreezeRed', 'default')
    replace('kwinrc', 'org.kde.kdecoration2', 'library',
            lambda v: read_key(config, 'kwinrc', 'org.kde.kdecoration2', 'theme') in ('__aurorae__svg__Amy-Light-Aurorae-6', '__aurorae__svg__Amy-Papirus-Dark'), 'org.kde.breeze')
    replace('kwinrc', 'org.kde.kdecoration2', 'theme', lambda v: v in ('__aurorae__svg__Amy-Light-Aurorae-6', '__aurorae__svg__Amy-Papirus-Dark'), 'Breeze')
    for version in ('gtk-3.0', 'gtk-4.0'):
        replace(version + '/settings.ini', 'Settings', 'gtk-icon-theme-name',
                lambda v: v in ('PapirusBreezeLight', 'PapirusBreezeDark'), 'breeze-dark' if dark else 'breeze')
    for key in ('LightThemeProfile', 'DarkThemeProfile'):
        replace('konsolerc', 'LightDarkTheme', key, lambda v: v in ('Papirus Breeze Light', 'Papirus Breeze Dark'), None)
    replace('konsolerc', 'Desktop Entry', 'DefaultProfile', lambda v: v in ('PapirusBreezeLight.profile', 'PapirusBreezeDark.profile'), None)
    wallpapers = [(data / ('wallpapers/' + name)).as_uri() for name in ('Moe', 'MoeDark')]
    def own_wallpaper(value):
        return any(value == uri or value.startswith(uri + '/') for uri in wallpapers)
    for key in ('Image', 'PreviewImage'):
        replace('kscreenlockerrc', 'Greeter][Wallpaper][org.kde.image][General', key,
                own_wallpaper, None)
    if live:
        # Reset only desktops still displaying our wallpaper, preserving panel layouts.
        candidates = [p / 'wallpapers/Next' for p in module_data_roots(data)]
        fallback = next((p.as_uri() for p in candidates if p.is_dir()), '')
        script = 'const owned = ' + json.dumps(wallpapers) + ';\nconst fallback = ' + json.dumps(fallback) + ';\n' + '''for (const d of desktops()) {
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    const image = String(d.readConfig("Image", ""));
    if (owned.some(uri => image === uri || image.startsWith(uri + "/"))) {
        d.writeConfig("Image", fallback);
    }
}'''
        backup.save(config / 'plasma-org.kde.plasma.desktop-appletsrc')
        subprocess.run(['qdbus6', 'org.kde.plasmashell', '/PlasmaShell',
                        'org.kde.PlasmaShell.evaluateScript', script], check=True)
        subprocess.run(['qdbus6', 'org.kde.KWin', '/KWin', 'org.kde.KWin.reconfigure'], check=True)
    startup = config / 'fish/config.fish'
    if startup.is_file():
        text = startup.read_text()
        begin, end = '# BEGIN Papirus Breeze terminal settings', '# END Papirus Breeze terminal settings'
        if begin in text and end in text:
            before, managed = text.split(begin, 1)
            after = managed.split(end, 1)[1]
            backup.save(startup)
            startup.write_text(before.rstrip('\n') + after)
    helper = config / 'fish/papirus-breeze.fish'
    if helper.is_file() and fingerprint(helper) in {
            fingerprint(ROOT / v / 'assets/fish/papirus-breeze.fish') for v in THEMES}:
        backup.save(helper)
        helper.unlink()


def module_data_roots(data):
    return [data] + [Path(p) for p in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if p]


def remove(data, config, state, dry_run=False, live=True):
    record_file = state / 'papirus-breeze/installation.json'
    if not record_file.exists():
        raise RuntimeError('No managed installation. First run: python3 install.py install')
    record = json.loads(record_file.read_text())
    if record['schema'] != 1 or record['data'] != str(data) or record['config'] != str(config):
        raise ValueError('The installation record does not match the selected directories.')
    allowed = assets()
    for relative in record['assets']:
        if relative not in allowed:
            raise ValueError('Unrecognized resource in the installation record: ' + relative)
        safe_target(data, relative)
    if live:
        # Removal needs native KDE tools, not the Papirus icon dependency.
        errors = [e for e in check(data, applying=True) if not e.startswith('Missing icon/cursor theme:')]
        if errors:
            raise RuntimeError('\n'.join(errors))
    restore_quick = {key: read_key(config, 'kdeglobals', 'KDE', key) == own
                     for key, own in QUICK.items()}
    print('Remove theme resources; preserve modified files, dependencies, and backups.')
    if dry_run:
        print('Dry run: no files changed.')
        return
    module = load_variant('light')
    backup = module.Backup(state, package='papirus-breeze')
    try:
        cleanup_config(data, config, backup, live)
        for key, own in QUICK.items():
            if restore_quick[key]:
                backup.save(config / 'kdeglobals')
                value = record['quick_previous'].get(key) or NATIVE[key]
                if value in THEMES.values():
                    value = NATIVE[key]
                if not any((p / 'plasma/look-and-feel' / value / 'metadata.json').is_file()
                           for p in module_data_roots(data)):
                    value = NATIVE[key]
                write_key(config, 'kdeglobals', 'KDE', key, value)
            if read_key(config, 'kdedefaults/kdeglobals', 'KDE', key) == own:
                backup.save(config / 'kdedefaults/kdeglobals')
                write_key(config, 'kdedefaults/kdeglobals', 'KDE', key, None)
        preserved = []
        for relative, expected in record['assets'].items():
            target = safe_target(data, relative)
            if not target.exists():
                continue
            if fingerprint(target) != expected:
                print('Preserved (modified after installation): ' + str(target))
                preserved.append(relative)
                continue
            backup.save(target)
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        backup.save(record_file)
        record_file.unlink()
    except Exception:
        restore_backup(backup.path)
        raise
    print('Removal complete. Quick Settings restored; reopen System Settings.')
    if preserved:
        print('Preserved customized resources: ' + str(len(preserved)))
    print('Backup: ' + str(backup.path))
    print('Administrative login integration, if installed, is removed separately (see docs).')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=('install', 'remove', 'check', 'status'),
                        help='install: install/update; remove: uninstall; check: prerequisites; status: installation state')
    parser.add_argument('--apply', choices=tuple(THEMES), help='apply Light or Dark after installation')
    parser.add_argument('--layout', action='store_true', help='with --apply, replace the current panels')
    parser.add_argument('--dry-run', action='store_true', help='simulate without changing files')
    for kind in ('data', 'config', 'state'):
        parser.add_argument('--' + kind + '-dir', type=Path, help='test destination; all three directories are required')
    args = parser.parse_args(argv)
    if not args.action:
        if not sys.stdin.isatty():
            parser.print_help()
            return 0
        print('Papirus Breeze\n1. Install/update\n2. Install and apply Light\n3. Install and apply Dark\n4. Remove\n5. Check prerequisites\n0. Exit')
        choice = input('Choose: ').strip()
        if choice == '0':
            return 0
        if choice not in ('1', '2', '3', '4', '5'):
            raise ValueError('Invalid choice.')
        args.action = {'1': 'install', '2': 'install', '3': 'install', '4': 'remove', '5': 'check'}[choice]
        if choice in ('2', '3'):
            args.apply = 'light' if choice == '2' else 'dark'
    alternate = any((args.data_dir, args.config_dir, args.state_dir))
    if alternate and not all((args.data_dir, args.config_dir, args.state_dir)):
        parser.error('Use --data-dir, --config-dir, and --state-dir together.')
    if args.apply and (args.action != 'install' or alternate):
        parser.error('--apply requires install in the real user directories.')
    if args.layout and not args.apply:
        parser.error('--layout requires --apply and replaces the current panels.')
    if os.geteuid() == 0:
        raise RuntimeError('Run as your normal user, without sudo.')
    directories = []
    for kind, fallback in (('data', '.local/share'), ('config', '.config'), ('state', '.local/state')):
        path = getattr(args, kind + '_dir') or Path(os.environ.get('XDG_' + kind.upper() + '_HOME', str(Path.home() / fallback)))
        directories.append(path.expanduser().resolve())
    data, config, state = directories
    if args.action == 'check':
        assets()
        errors = check(data, applying=not alternate)
        for error in errors:
            print('Prerequisite: ' + error)
        print('Check failed; see docs/INSTALLATION.md.' if errors else 'Integrity and prerequisites: OK.')
        return bool(errors)
    if args.action == 'status':
        print('Managed installation: ' + ('yes' if (state / 'papirus-breeze/installation.json').exists() else 'no'))
        for key in QUICK:
            print(key + ': ' + read_key(config, 'kdeglobals', 'KDE', key))
        return 0
    if args.action == 'install':
        install(data, config, state, args.apply, args.layout, args.dry_run)
    else:
        remove(data, config, state, args.dry_run, live=not alternate)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        sys.exit(1)
