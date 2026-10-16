# SPDX-License-Identifier: GPL-3.0-only
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('unified_installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


@unittest.skipUnless(shutil.which('kreadconfig6') and shutil.which('kwriteconfig6'), 'KConfig 6 tools are missing')
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data, self.config, self.state = [self.base / p for p in ('share', 'config', 'state')]
        self.source = self.base / 'source'
        self.source.mkdir()
        self.sources = {}
        for variant, theme in installer.THEMES.items():
            source = self.source / variant
            source.mkdir()
            (source / 'metadata.json').write_text(json.dumps({'KPlugin': {'Id': theme}}))
            self.sources['plasma/look-and-feel/' + theme] = source
        profile = self.source / 'PapirusBreezeLight.profile'
        profile.write_text('[General]\nName=Papirus Breeze Light\n')
        self.sources['konsole/PapirusBreezeLight.profile'] = profile
        self.addCleanup(patch.stopall)
        patch.object(installer, 'assets', return_value=self.sources).start()
        self.original_check = installer.check
        patch.object(installer, 'check', return_value=[]).start()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def install(self, **kwargs):
        installer.install(self.data, self.config, self.state, **kwargs)

    def remove(self, **kwargs):
        installer.remove(self.data, self.config, self.state, live=False, **kwargs)

    def read(self, key):
        return installer.read_key(self.config, 'kdeglobals', 'KDE', key)

    def test_install_upgrade_remove_restores_previous_pair_and_preserves_other_settings(self):
        for key in installer.QUICK:
            theme = 'previous.' + key
            folder = self.data / 'plasma/look-and-feel' / theme
            folder.mkdir(parents=True)
            (folder / 'metadata.json').write_text('{}')
            installer.write_key(self.config, 'kdeglobals', 'KDE', key, theme)
        self.install()
        self.install()  # Updating must not replace the original Quick Settings selection.
        for key, theme in installer.QUICK.items():
            self.assertEqual(self.read(key), theme)
        installer.write_key(self.config, 'kdeglobals', 'General', 'font', 'My font 12')
        self.remove()
        for key in installer.QUICK:
            self.assertEqual(self.read(key), 'previous.' + key)
        self.assertEqual(installer.read_key(self.config, 'kdeglobals', 'General', 'font'), 'My font 12')
        self.assertFalse((self.state / 'papirus-breeze/installation.json').exists())
        for relative in self.sources:
            self.assertFalse((self.data / relative).exists())

    def test_remove_preserves_modified_assets_and_unrelated_profiles(self):
        self.install()
        theme = self.data / next(iter(self.sources))
        (theme / 'custom.txt').write_text('personal')
        unrelated = self.data / 'konsole/Personal.profile'
        unrelated.write_text('keep')
        self.remove()
        self.assertEqual((theme / 'custom.txt').read_text(), 'personal')
        self.assertEqual(unrelated.read_text(), 'keep')
        self.assertFalse((self.data / 'konsole/PapirusBreezeLight.profile').exists())

    def test_remove_does_not_overwrite_later_quick_settings_choices(self):
        self.install()
        installer.write_key(self.config, 'kdeglobals', 'KDE', 'DefaultLightLookAndFeel', 'new.user.theme')
        self.remove()
        self.assertEqual(self.read('DefaultLightLookAndFeel'), 'new.user.theme')
        self.assertEqual(self.read('DefaultDarkLookAndFeel'), installer.NATIVE['DefaultDarkLookAndFeel'])

    def test_failure_restores_assets_and_configuration(self):
        old = self.data / next(iter(self.sources))
        old.mkdir(parents=True)
        (old / 'metadata.json').write_text('original')
        installer.write_key(self.config, 'kdeglobals', 'KDE', 'Unrelated', 'keep')
        original_config = (self.config / 'kdeglobals').read_bytes()
        original_write = installer.write_key
        def fail_second(config, filename, group, key, value):
            if key == 'DefaultDarkLookAndFeel':
                raise RuntimeError('simulated write failure')
            original_write(config, filename, group, key, value)
        with patch.object(installer, 'write_key', side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, 'simulated'):
                self.install()
        self.assertEqual((old / 'metadata.json').read_text(), 'original')
        self.assertEqual((self.config / 'kdeglobals').read_bytes(), original_config)
        self.assertFalse((self.state / 'papirus-breeze/installation.json').exists())

    def test_remove_cleans_managed_fish_block_but_keeps_user_settings(self):
        self.install()
        fish = self.config / 'fish/config.fish'
        fish.parent.mkdir(parents=True)
        fish.write_text('set -g personal before\n\n# BEGIN Papirus Breeze terminal settings\nsource managed\n# END Papirus Breeze terminal settings\nset -g personal after\n')
        installer.write_key(self.config, 'konsolerc', 'Desktop Entry', 'DefaultProfile', 'Personal.profile')
        self.remove()
        self.assertNotIn('source managed', fish.read_text())
        self.assertIn('set -g personal before', fish.read_text())
        self.assertIn('set -g personal after', fish.read_text())
        self.assertEqual(installer.read_key(self.config, 'konsolerc', 'Desktop Entry', 'DefaultProfile'), 'Personal.profile')

    def test_dry_run_does_not_create_destination_directories(self):
        self.install(dry_run=True)
        self.assertFalse(self.data.exists())
        self.assertFalse(self.config.exists())
        self.assertFalse(self.state.exists())

    def test_removal_refuses_traversal_in_state_before_changing_config(self):
        self.install()
        record_file = self.state / 'papirus-breeze/installation.json'
        record = json.loads(record_file.read_text())
        record['assets']['../outside'] = 'invalid'
        record_file.write_text(json.dumps(record))
        before = (self.config / 'kdeglobals').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Unrecognized'):
            self.remove()
        self.assertEqual((self.config / 'kdeglobals').read_bytes(), before)

    def test_install_refuses_symbolic_asset_parent(self):
        self.data.mkdir()
        outside = self.base / 'outside'
        outside.mkdir()
        (self.data / 'plasma').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symbolic'):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_live_removal_switches_to_native_theme_before_deleting_assets(self):
        self.install()
        installer.write_key(self.config, 'kdeglobals', 'KDE', 'LookAndFeelPackage', installer.THEMES['dark'])
        installer.write_key(self.config, 'kdeglobals', 'General', 'ColorScheme', 'PapirusBreezeDark')
        panels = self.config / 'plasma-org.kde.plasma.desktop-appletsrc'
        panels.write_text('personal panel layout')
        run = installer.subprocess.run
        commands = []
        def native_command(command, **kwargs):
            if command[0] in ('plasma-apply-lookandfeel', 'qdbus6'):
                self.assertTrue((self.data / next(iter(self.sources))).exists())
                commands.append(command)
                return installer.subprocess.CompletedProcess(command, 0)
            return run(command, **kwargs)
        with patch.object(installer.subprocess, 'run', side_effect=native_command):
            installer.remove(self.data, self.config, self.state, live=True)
        self.assertIn(['plasma-apply-lookandfeel', '--apply', 'org.kde.breezedark.desktop'], commands)
        self.assertEqual(self.read('LookAndFeelPackage'), 'org.kde.breezedark.desktop')
        self.assertEqual(panels.read_text(), 'personal panel layout')
        self.assertFalse((self.data / next(iter(self.sources))).exists())

    def test_dependency_check_accepts_user_icons_with_an_isolated_destination(self):
        user_data = self.base / 'user-share'
        dependency = 'Missing icon/cursor theme: Papirus'
        module = types.SimpleNamespace(dependency_errors=lambda data, applying=False: [] if data == user_data else [dependency])
        with patch.dict(os.environ, {'XDG_DATA_HOME': str(user_data)}), \
                patch.object(installer, 'load_variant', return_value=module):
            errors = self.original_check(self.data)
        self.assertNotIn(dependency, errors)
