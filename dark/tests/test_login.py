# SPDX-License-Identifier: GPL-3.0-only
import configparser
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('login_integration', ROOT / 'scripts/login.py')
login = importlib.util.module_from_spec(spec)
spec.loader.exec_module(login)


class LoginTests(unittest.TestCase):
    def test_palette_matches_light_dark_in_complementary_greeter(self):
        variant = 'dark' if json.loads((ROOT / 'manifest.json').read_text())['name'].endswith('Dark') else 'light'
        palette = login.login_palette(ROOT, variant)
        self.assertEqual(dict(palette['Colors:Complementary']), dict(palette['Colors:Window']))
        self.assertEqual(palette['General']['AccentColor'], '233,61,88')
        self.assertEqual(palette['Icons']['Theme'], 'PapirusBreeze' + variant.title())
        self.assertEqual(palette['KDE']['LookAndFeelPackage'], 'org.kde.breeze.desktop')

    def test_follow_accepts_only_known_theme_data_and_no_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'kdeglobals'
            for variant in ('light', 'dark'):
                source.write_text('[General]\nColorScheme=PapirusBreeze' + variant.title() + '\n')
                self.assertEqual(login.selected_variant(source, os.getuid()), variant)
            source.write_text('[General]\nColorScheme=OtherTheme\n[KDE]\nLookAndFeelPackage=com.delta.papirus-breeze-light\n')
            self.assertIsNone(login.selected_variant(source))
            alias = Path(directory) / 'alias'
            alias.symlink_to(source)
            self.assertIsNone(login.selected_variant(alias))
            source.write_text('[KDE]\nLookAndFeelPackage=com.delta.papirus-breeze-dark\n')
            self.assertEqual(login.selected_variant(source), 'dark')

    def test_merge_preserves_authentication_and_other_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'plasmalogin.conf'
            config.write_text('[Autologin]\nUser=keep-user\nSession=keep-session\n')
            login.set_values(config, {'Greeter': {'WallpaperPluginId': 'org.kde.image'}})
            merged = login.config_file(config)
            self.assertEqual(merged['Autologin']['User'], 'keep-user')
            self.assertEqual(merged['Autologin']['Session'], 'keep-session')
            self.assertEqual(merged['Greeter']['WallpaperPluginId'], 'org.kde.image')

    def test_privileged_writer_refuses_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'original'
            original.write_text('[Keep]\nValue=untouched\n')
            alias = Path(directory) / 'symlink'
            alias.symlink_to(original)
            with self.assertRaises(RuntimeError):
                login.set_values(alias, {'Test': {'Key': 'value'}})
            self.assertEqual(original.read_text(), '[Keep]\nValue=untouched\n')

    def test_automatic_apply_preserves_session_and_skips_same_palette(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            store = base / 'store'
            profile = store / 'profiles/light'
            profile.mkdir(parents=True)
            (profile / 'profile.json').write_text(json.dumps({'manager': 'plasma-login', 'image': '/installed/light.png', 'cursor': 'breeze_cursors'}))
            for name, groups in {'kdeglobals': {'General': {'ColorScheme': 'PapirusBreezeLoginLight'}},
                                 'plasmarc': {'Theme': {'name': 'PapirusBreezeRed'}},
                                 'kcminputrc': {'Mouse': {'cursorTheme': 'breeze_cursors'}}}.items():
                login.set_values(profile / name, groups)
            config_root = base / 'etc'
            config_root.mkdir()
            config = config_root / 'plasmalogin.conf'
            config.write_text('[Autologin]\nSession=keep\n')
            account = types.SimpleNamespace(pw_dir=str(base / 'greeter'), pw_uid=os.getuid(), pw_gid=os.getgid())
            with patch.object(login, 'STORE', store), patch.object(login, 'STATE', base / 'state/current.json'), \
                    patch.object(login, 'CONFIG_ROOT', config_root), patch.object(login.pwd, 'getpwnam', return_value=account):
                self.assertTrue(login.apply_variant('light', 'plasma-login'))
                self.assertFalse(login.apply_variant('light', 'plasma-login'))
            merged = login.config_file(config)
            self.assertEqual(merged['Autologin']['Session'], 'keep')
            self.assertEqual(merged['Greeter][Wallpaper][org.kde.image][General']['Image'], 'file:///installed/light.png')
            self.assertEqual(login.config_file(base / 'greeter/.config/kdeglobals')['General']['ColorScheme'], 'PapirusBreezeLoginLight')
            self.assertFalse((base / 'greeter/.config/konsolerc').exists())

    def test_sddm_appearance_has_priority_and_preserves_autologin(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            profile = base / 'store/profiles/dark'
            profile.mkdir(parents=True)
            (profile / 'profile.json').write_text(json.dumps({'manager': 'sddm', 'image': '/installed/dark.png', 'cursor': 'Breeze_Light'}))
            for name in ('kdeglobals', 'plasmarc', 'kcminputrc'):
                login.set_values(profile / name, {'General': {'Name': 'test'}})
            etc = base / 'etc'; etc.mkdir()
            (etc / 'sddm.conf').write_text('[Autologin]\nUser=keep\nSession=plasma\n[Theme]\nCurrent=old\n')
            account = types.SimpleNamespace(pw_dir=str(base / 'greeter'), pw_uid=os.getuid(), pw_gid=os.getgid())
            with patch.object(login, 'STORE', base / 'store'), patch.object(login, 'STATE', base / 'state/current.json'), \
                    patch.object(login, 'CONFIG_ROOT', etc), patch.object(login.pwd, 'getpwnam', return_value=account):
                self.assertTrue(login.apply_variant('dark', 'sddm'))
            config = login.config_file(etc / 'sddm.conf')
            self.assertEqual(config['Theme']['Current'], 'papirus-breeze-dark')
            self.assertEqual(config['Theme']['CursorTheme'], 'Breeze_Light')
            self.assertEqual(config['Autologin']['User'], 'keep')
            self.assertEqual(config['Autologin']['Session'], 'plasma')

    @unittest.skipUnless(__import__('shutil').which('systemd-analyze'), 'systemd-analyze is not installed')
    def test_follow_units_pass_systemd_validation(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for name, contents in login.unit_contents(Path('/home/example/.config/kdeglobals')).items():
                path = Path(directory) / name
                path.write_text(contents)
                paths.append(str(path))
            result = subprocess.run(['systemd-analyze', 'verify', '--man=no', *paths], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_dry_run_does_not_install_or_enable_services(self):
        import sys
        with patch.object(login, 'provision') as provision, patch.object(login, 'follow_user') as follow, \
                patch.object(login, 'detect_manager', return_value='plasma-login'), \
                patch.object(login.pwd, 'getpwnam'), patch.object(login.subprocess, 'run') as run:
            self.assertEqual(login.main(ROOT, ['--follow-user', 'example', '--dry-run']), 0)
            provision.assert_not_called()
            follow.assert_not_called()
            run.assert_not_called()
