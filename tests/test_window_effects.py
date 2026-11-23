"""Exercise the optional effects profile and its recovery paths."""
import configparser
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('window_effects', ROOT / 'tools/window-effects.py')
effects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(effects)


class DefaultRoundingTests(unittest.TestCase):
    def test_both_themes_exclude_chatgpt_from_rounded_corners(self):
        for variant in ('light', 'dark'):
            with self.subTest(variant=variant):
                package = ROOT / variant
                settings = json.loads((package / 'config/settings.json').read_text())
                exclusions = settings['kwinrc']['Round-Corners']['Exclusions']
                defaults = configparser.ConfigParser()
                defaults.read(package / 'assets/plasma/look-and-feel' /
                              f'com.delta.papirus-breeze-{variant}/contents/defaults')
                self.assertIn('chatgpt', exclusions.split(','))
                self.assertEqual(defaults['kwinrc][Round-Corners']['Exclusions'], exclusions)


@unittest.skipUnless(shutil.which('kreadconfig6') and shutil.which('kwriteconfig6'),
                     'KConfig 6 tools are missing')
class ProfileTests(unittest.TestCase):
    rule = 'papirus-breeze-chatgpt'
    blur = ('kwinrc', 'Effect-blurplus')
    exclusions = ('kwinrc', 'Round-Corners', 'Exclusions')
    order = ('kwinrulesrc', 'General', 'Order')

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        config = root / 'config'
        config.mkdir()
        state = root / 'state'
        self.snapshot = state / 'papirus-breeze/window-effects.json'
        environment = patch.dict(effects.os.environ, XDG_CONFIG_HOME=str(config),
                                 XDG_CONFIG_DIRS=str(config), XDG_STATE_HOME=str(state),
                                 XDG_SESSION_TYPE='wayland')
        self.addCleanup(environment.stop)
        environment.start()
        for target, attribute, options in (
            (effects.os, 'geteuid', {'return_value': 1000}),
            (effects, 'command', {'side_effect': self.run_without_kwin}),
            (effects, 'effect', {'return_value': 'true'}),
        ):
            mock = patch.object(target, attribute, **options)
            self.addCleanup(mock.stop)
            mock.start()

    @staticmethod
    def run_without_kwin(*args):
        if args[0] == 'qdbus6':
            return ''
        return subprocess.check_output(args, text=True).rstrip('\n')

    def run_action(self, *args):
        with patch.object(effects.sys, 'argv', ['window-effects.py', *args]):
            effects.main()

    def read(self, key):
        return effects.setting('kreadconfig6', key, '--default', effects.MISSING)

    def test_default_profile_leaves_chatgpt_out(self):
        self.run_action('apply')

        for key in ('WindowClasses', 'DecorWindowClasses'):
            self.assertNotIn('Chatgpt', self.read((*self.blur, key)).splitlines())
        self.assertIn('chatgpt', self.read(self.exclusions).split(','))
        self.assertNotIn(self.rule, self.read(self.order).split(','))

    def test_chatgpt_opt_in_and_restore_preserve_previous_choices(self):
        opacity = ('kwinrulesrc', self.rule, 'opacityactive')
        original_blur = 'example.one\nexample.two'
        original_order = 'user-rule,' + self.rule
        for key, value in ((opacity, '94'), (self.order, original_order),
                           (self.exclusions, 'user-exclusion,chatgpt'),
                           ((*self.blur, 'DecorWindowClasses'), original_blur)):
            effects.setting('kwriteconfig6', key, value)

        self.run_action('apply', '--chatgpt')

        for key in ('WindowClasses', 'DecorWindowClasses'):
            classes = self.read((*self.blur, key)).splitlines()
            self.assertIn('Chatgpt', classes)
            self.assertIn('org.kde.dolphin', classes)
        self.assertEqual(self.read(self.exclusions), 'dolphin,konsole')
        self.assertEqual(self.read(('kwinrulesrc', self.rule, 'wmclass')), 'Chatgpt')
        self.assertEqual(self.read(opacity), '90')
        self.assertEqual(self.read(('kwinrulesrc', self.rule, 'opacityinactive')), '90')
        self.assertEqual(self.read(self.order).split(',').count(self.rule), 1)

        self.run_action('restore')

        self.assertEqual(self.read(opacity), '94')
        self.assertEqual(self.read(('kwinrulesrc', self.rule, 'opacityinactive')), effects.MISSING)
        self.assertEqual(self.read(self.order), original_order)
        self.assertEqual(self.read(self.exclusions), 'user-exclusion,chatgpt')
        self.assertEqual(self.read((*self.blur, 'DecorWindowClasses')), original_blur)
        self.assertFalse(self.snapshot.exists())


class UpgradeTests(unittest.TestCase):
    def test_no_packages_does_not_change_session(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(effects, 'command', return_value='kwin'), patch.object(effects.subprocess, 'run') as run, patch.object(effects, 'setting') as setting:
            effects.prepare_upgrade(Path(tmp))
            run.assert_not_called()
            setting.assert_not_called()
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_auth_failure_leaves_session_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(effects, 'command', return_value='kwin-effects-glass-local'), patch.object(effects.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'sudo')), patch.object(effects, 'setting') as setting:
            with self.assertRaises(subprocess.CalledProcessError):
                effects.prepare_upgrade(Path(tmp))
            setting.assert_not_called()
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_removal_failure_preserves_backup_and_dependency_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / 'config'
            config.mkdir()
            (config / 'kwinrc').write_text('original settings')
            state = root / 'state'
            packages = ['kwin-effect-rounded-corners', 'kwin-effects-glass-local']
            def command(*args):
                return '\n'.join(packages) if args == ('pacman', '-Qq') else 'versions'
            with patch.dict(effects.os.environ, XDG_CONFIG_HOME=str(config)), patch.object(effects, 'command', side_effect=command), patch.object(effects, 'effect', return_value='true'), patch.object(effects, 'setting') as setting, patch.object(effects.subprocess, 'run', side_effect=[None, subprocess.CalledProcessError(1, 'pacman')]) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    effects.prepare_upgrade(state)
                run.assert_called_with(['sudo', 'pacman', '-R', *packages], check=True)
                setting.assert_any_call('kwriteconfig6', ('kwinrc', 'Plugins', 'glassEnabled'), 'false')
            backup, = (state / 'papirus-breeze').glob('kwin-upgrade-*')
            self.assertEqual((backup / 'kwinrc').read_text(), 'original settings')
            self.assertTrue((backup / 'packages.txt').exists())
