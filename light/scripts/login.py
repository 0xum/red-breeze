#!/usr/bin/env python3
"""Provision a matching greeter and optionally follow one user's Papirus palette."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile

STORE = Path('/usr/local/share/papirus-breeze-login')
SETTINGS = Path('/etc/papirus-breeze-login.json')
RUNTIME = Path('/usr/local/libexec/papirus-breeze-login.py')
SERVICE = 'papirus-breeze-login.service'
PATH_UNIT = 'papirus-breeze-login.path'
STATE = Path('/var/lib/papirus-breeze-login/current.json')
CONFIG_ROOT = Path('/etc')
VARIANTS = ('light', 'dark')


def config_file(path):
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    if path.is_symlink():
        raise RuntimeError("Symbolic configuration file refused: " + str(path))
    if path.exists():
        config.read_string(path.read_text())
    return config


def write_config(path, config):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.papirus-', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            config.write(stream, space_around_delimiters=False)
            stream.flush()
            temporary.chmod(0o644)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def set_values(path, groups):
    config = config_file(path)
    for group, values in groups.items():
        if not config.has_section(group):
            config.add_section(group)
        for key, value in values.items():
            config.set(group, key, str(value))
    write_config(path, config)


def detect_manager():
    name = Path('/etc/systemd/system/display-manager.service').resolve().name
    if name == 'plasmalogin.service':
        return 'plasma-login'
    if name == 'sddm.service':
        return 'sddm'
    raise RuntimeError('Login manager not detected; specify --manager plasma-login or sddm.')


def selected_variant(source, uid=None):
    # Read data only. Never import code or accept paths/commands from this file.
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 1024 * 1024:
        return None
    if uid is not None and source.stat().st_uid != uid:
        return None
    config = config_file(source)
    scheme = config.get('General', 'ColorScheme', fallback='')
    for variant in VARIANTS:
        if scheme == 'PapirusBreeze' + variant.title():
            return variant
    if not scheme:
        theme = config.get('KDE', 'LookAndFeelPackage', fallback='')
        for variant in VARIANTS:
            if theme == 'com.delta.papirus-breeze-' + variant:
                return variant
    return None


def login_palette(package, variant):
    palette = config_file(package / f'assets/color-schemes/PapirusBreeze{variant.title()}.colors')
    # Both native greeters use Complementary. Match Window so Light stays light.
    palette['Colors:Complementary'] = dict(palette['Colors:Window'])
    palette['General']['ColorScheme'] = 'PapirusBreezeLogin' + variant.title()
    palette['General']['Name'] = 'Papirus Breeze Login ' + variant.title()
    palette['General']['AccentColor'] = '233,61,88'
    palette['General']['font'] = 'Noto Sans,10,-1,5,50,0,0,0,0,0'
    palette['KDE'] = {'widgetStyle': 'Breeze', 'LookAndFeelPackage': 'org.kde.breeze.desktop'}
    palette['Icons'] = {'Theme': 'PapirusBreeze' + variant.title()}
    return palette


def readable_tree(path):
    # Installed by root; readable by the greeter without opening the user's home.
    for item in [path, *path.rglob('*')]:
        if not item.is_symlink():
            item.chmod(0o755 if item.is_dir() else 0o644)


def provision(package, variant, manager, backup, account):
    from install import copy_asset
    data = Path(account.pw_dir) / '.local/share'
    for directory in (STORE, STORE / 'profiles', STORE / 'wallpapers'):
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(0o755)
    # Copy only the themes provided here. Breeze/hicolor remain system fallbacks.
    assets = (f'icons/PapirusBreeze{variant.title()}', 'plasma/desktoptheme/PapirusBreezeRed')
    for relative in assets:
        copy_asset(package / 'assets' / relative, data / relative, backup)
        readable_tree(data / relative)
    wallpaper_name = 'Moe' if variant == 'light' else 'MoeDark'
    wallpaper = STORE / 'wallpapers' / wallpaper_name
    copy_asset(package / 'assets/wallpapers' / wallpaper_name, wallpaper, backup)
    readable_tree(wallpaper)
    # Greeter-only palette leaves the desktop's complementary colors unchanged.
    palette = login_palette(package, variant)
    scheme = 'PapirusBreezeLogin' + variant.title()
    scheme_file = data / 'color-schemes' / (scheme + '.colors')
    backup.save(scheme_file)
    write_config(scheme_file, palette)
    payload = STORE / 'profiles' / variant
    backup.save(payload)
    payload.mkdir(parents=True, exist_ok=True)
    write_config(payload / 'kdeglobals', palette)
    cursor = 'breeze_cursors' if variant == 'light' else 'Breeze_Light'
    set_values(payload / 'kcminputrc', {'Mouse': {'cursorTheme': cursor, 'cursorSize': '18'}})
    set_values(payload / 'plasmarc', {'Theme': {'name': 'PapirusBreezeRed'}})
    image = wallpaper / ('contents/images/3073x1420.png' if variant == 'light' else 'contents/images_dark/1844x853.png')
    profile = {'variant': variant, 'manager': manager, 'image': str(image), 'cursor': cursor}
    (payload / 'profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    readable_tree(payload)
    if manager == 'sddm':
        theme = Path('/usr/share/sddm/themes') / ('papirus-breeze-' + variant)
        copy_asset(Path('/usr/share/sddm/themes/breeze'), theme, backup)
        set_values(theme / 'theme.conf.user', {'General': {'background': str(image), 'type': 'image', 'showlogo': 'hidden', 'showClock': 'true'}})
        readable_tree(theme)
    # Intermediate data/config directories may be newly created under a private home.
    for directory in (Path(account.pw_dir) / '.local', data, data / 'icons', data / 'plasma', data / 'plasma/desktoptheme', data / 'color-schemes'):
        if directory.exists():
            directory.chmod(0o755)
            os.chown(directory, account.pw_uid, account.pw_gid)


def apply_variant(variant, manager, backup=None, force=False):
    if variant not in VARIANTS:
        raise ValueError('Invalid variant')
    profile_dir = STORE / 'profiles' / variant
    profile = json.loads((profile_dir / 'profile.json').read_text())
    if profile['manager'] != manager:
        raise RuntimeError('Reinstall profiles for the active login manager.')
    signature = hashlib.sha256(b''.join((profile_dir / name).read_bytes() for name in ('profile.json', 'kdeglobals', 'plasmarc', 'kcminputrc'))).hexdigest()
    if not force and STATE.exists():
        current = json.loads(STATE.read_text())
        if current == {'variant': variant, 'signature': signature, 'manager': manager}:
            return False
    account = pwd.getpwnam('plasmalogin' if manager == 'plasma-login' else 'sddm')
    home = Path(account.pw_dir)
    config_dir = home / '.config'
    config_dir.mkdir(parents=True, exist_ok=True)
    os.chown(config_dir, account.pw_uid, account.pw_gid)
    for name in ('kdeglobals', 'plasmarc', 'kcminputrc'):
        target = config_dir / name
        if backup:
            backup.save(target)
        payload = config_file(profile_dir / name)
        set_values(target, {section: dict(payload[section]) for section in payload.sections()})
        os.chown(target, account.pw_uid, account.pw_gid)
    if manager == 'plasma-login':
        target = CONFIG_ROOT / 'plasmalogin.conf'
        groups = {'Greeter': {'WallpaperPluginId': 'org.kde.image', 'ShowClock': 'true'},
                  'Greeter][Wallpaper][org.kde.image][General': {'Image': Path(profile['image']).as_uri(), 'PreviewImage': Path(profile['image']).as_uri()}}
    else:
        # Main config has priority over older variant-specific conf.d files.
        target = CONFIG_ROOT / 'sddm.conf'
        groups = {'Theme': {'Current': 'papirus-breeze-' + variant, 'CursorTheme': profile['cursor'], 'CursorSize': '18'}}
    if backup:
        backup.save(target)
    set_values(target, groups)
    # Native KCM also clears greeter caches when synchronizing its palette.
    if (home / '.cache').is_dir():
        shutil.rmtree(home / '.cache')
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({'variant': variant, 'signature': signature, 'manager': manager}, indent=2) + '\n')
    print('Login aplicado: Papirus Breeze ' + variant.title(), flush=True)
    return True


def sync():
    settings = json.loads(SETTINGS.read_text())
    user = pwd.getpwnam(settings['user'])
    variant = selected_variant(Path(settings['source']), user.pw_uid)
    if variant is None:
        print('Not a Papirus Breeze theme; login appearance preserved.')
        return
    if not (STORE / 'profiles' / variant / 'profile.json').is_file():
        raise RuntimeError('Variant not installed for login: ' + variant)
    apply_variant(variant, settings['manager'])


def unit_contents(source):
    return {
        SERVICE: '[Unit]\nDescription=Synchronize Papirus Breeze login appearance\nAfter=local-fs.target\nBefore=display-manager.service\n\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 /usr/local/libexec/papirus-breeze-login.py --sync\n\n[Install]\nWantedBy=multi-user.target\n',
        PATH_UNIT: '[Unit]\nDescription=Watch the selected Papirus Breeze user palette\n\n[Path]\nPathChanged=' + str(source) + '\nUnit=' + SERVICE + '\n\n[Install]\nWantedBy=multi-user.target\n',
    }


def follow_user(username, manager, backup, runtime_source):
    from install import copy_asset
    user = pwd.getpwnam(username)
    if user.pw_uid == 0:
        raise ValueError('Choose the graphical session user, not root.')
    source = Path(user.pw_dir) / '.config/kdeglobals'
    if not source.is_file():
        raise RuntimeError('Session kdeglobals not found: ' + str(source))
    if any(char in str(source) for char in ('\n', '\r', '%', '\\')):
        raise ValueError('Path is incompatible with the systemd unit')
    backup.save(SETTINGS)
    SETTINGS.write_text(json.dumps({'source': str(source), 'manager': manager, 'user': username}, indent=2) + '\n')
    SETTINGS.chmod(0o644)
    copy_asset(runtime_source, RUNTIME, backup)
    RUNTIME.chmod(0o755)
    units = unit_contents(source)
    for name, content in units.items():
        path = Path('/etc/systemd/system') / name
        backup.save(path)
        path.write_text(content)
        path.chmod(0o644)
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', SERVICE], check=True)
    subprocess.run(['systemctl', 'enable', '--now', PATH_UNIT], check=True)
    # Calling sync directly preserves the installation's backup for the first apply.
    variant = selected_variant(source, user.pw_uid)
    if variant is not None and (STORE / 'profiles' / variant / 'profile.json').exists():
        apply_variant(variant, manager, backup, force=True)
    print('Automatic theme following enabled for ' + username + '.', flush=True)


def main(package=None, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manager', choices=('auto', 'plasma-login', 'sddm'), default='auto')
    parser.add_argument('--follow-user', help="follow this user's Light/Dark changes through systemd.path")
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--sync', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.sync:
        if os.geteuid() != 0:
            raise RuntimeError('Synchronization runs through the installed administrative service.')
        sync()
        return 0
    if package is None:
        parser.error('Use the package install-login.py script for installation.')
    from install import Backup, verify_assets
    verify_assets()
    manager = detect_manager() if args.manager == 'auto' else args.manager
    account = pwd.getpwnam('plasmalogin' if manager == 'plasma-login' else 'sddm')
    variant = 'dark' if json.loads((package / 'manifest.json').read_text())['name'].endswith('Dark') else 'light'
    if manager == 'sddm' and not Path('/usr/share/sddm/themes/breeze/Main.qml').is_file():
        raise RuntimeError('Install the SDDM Breeze theme before continuing.')
    print(f'Install login appearance {variant} for {manager}: palette, icons, cursor, and wallpaper.')
    if args.follow_user:
        print('Follow the palette of ' + args.follow_user + '; install the systemd service and watcher.')
    print('The login manager will not restart; authentication and session settings are preserved.')
    if args.dry_run:
        print('Dry run complete. No files changed.')
        return 0
    if os.geteuid() != 0:
        raise RuntimeError('Run with sudo or pkexec to configure the login account.')
    backup = Backup(Path('/var/lib'))
    try:
        backup.save(STATE)
        provision(package, variant, manager, backup, account)
        if args.follow_user:
            follow_user(args.follow_user, manager, backup, Path(__file__).resolve())
        else:
            apply_variant(variant, manager, backup, force=True)
    finally:
        if backup.path.exists():
            print('Backup:', backup.path, flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError, configparser.Error, subprocess.CalledProcessError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        sys.exit(1)
