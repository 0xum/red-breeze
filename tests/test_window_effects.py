"""Upgrade preparation must preserve recovery data and stop on failures."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('window_effects', Path(__file__).resolve().parents[1] / 'tools/window-effects.py')
effects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(effects)


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
