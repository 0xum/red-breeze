"""Native effect installation must preserve existing binaries and recovery state."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inner_corners', ROOT / 'light/scripts/inner_corners.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        query = patch.object(native.subprocess, 'check_output', return_value='false')
        query.start()
        self.addCleanup(query.stop)
        self.base = Path(self.temp.name)
        self.state = self.base / 'state'
        self.target = self.base / 'plugins' / (native.EFFECT + '.so')
        self.target.parent.mkdir()
        self.target.write_bytes(b'previous plugin')

    def command(self, args, **kwargs):
        if args[0] == 'cmake' and '--build' in args:
            binary = self.state / 'build-6.8.3/plugins/kwin/effects/plugins' / (native.EFFECT + '.so')
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'new plugin')
        if args[:2] == ['pkexec', '/usr/bin/install']:
            shutil.copy2(args[-2], args[-1])

    def test_install_update_remove_restores_original_and_skips_matching_build(self):
        with patch.object(native.shutil, 'which', return_value='/usr/bin/cmake'), \
                patch.object(native.subprocess, 'run', side_effect=self.command) as run:
            native.install(self.state, self.target, '6.8.3', 'cmake')
            self.assertEqual(self.target.read_bytes(), b'new plugin')
            run.reset_mock()
            native.install(self.state, self.target, '6.8.3', 'cmake')
            run.assert_not_called()
            native.remove(self.state)
        self.assertEqual(self.target.read_bytes(), b'previous plugin')
        self.assertFalse((self.state / 'native-inner-corners.json').exists())

    def test_authorization_failure_preserves_binary_and_does_not_claim_installation(self):
        def fail(args, **kwargs):
            if args[0] == 'pkexec':
                raise subprocess.CalledProcessError(1, args)
            self.command(args, **kwargs)
        with patch.object(native.shutil, 'which', return_value='/usr/bin/cmake'), \
                patch.object(native.subprocess, 'run', side_effect=fail) as run, \
                patch.object(native.subprocess, 'check_output', return_value='true'):
            with self.assertRaises(subprocess.CalledProcessError):
                native.install(self.state, self.target, '6.8.3', 'cmake')
            run.assert_any_call(['qdbus6', 'org.kde.KWin', '/Effects', 'loadEffect', native.EFFECT], check=True)
        self.assertEqual(self.target.read_bytes(), b'previous plugin')
        self.assertFalse((self.state / 'native-inner-corners.json').exists())

    def test_remove_preserves_a_modified_plugin(self):
        with patch.object(native.shutil, 'which', return_value='/usr/bin/cmake'), \
                patch.object(native.subprocess, 'run', side_effect=self.command):
            native.install(self.state, self.target, '6.8.3', 'cmake')
        self.target.write_bytes(b'user modification')
        with patch.object(native.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'modified'):
                native.remove(self.state)
            run.assert_not_called()
        self.assertEqual(self.target.read_bytes(), b'user modification')
        self.assertTrue((self.state / 'native-inner-corners.json').exists())

    def test_update_preserves_a_modified_plugin_without_building_or_authenticating(self):
        with patch.object(native.shutil, 'which', return_value='/usr/bin/cmake'), \
                patch.object(native.subprocess, 'run', side_effect=self.command):
            native.install(self.state, self.target, '6.8.3', 'cmake')
        self.target.write_bytes(b'user modification')
        with patch.object(native.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'modified'):
                native.install(self.state, self.target, '6.8.3', 'cmake')
            run.assert_not_called()
        self.assertEqual(self.target.read_bytes(), b'user modification')

    def test_both_standalone_variants_ship_identical_native_sources_and_helper(self):
        relative = Path('assets/kwin/papirus-inner-corners')
        for source in (ROOT / 'light' / relative).iterdir():
            self.assertEqual(source.read_bytes(), (ROOT / 'dark' / relative / source.name).read_bytes())
        self.assertEqual((ROOT / 'light/scripts/inner_corners.py').read_bytes(),
                         (ROOT / 'dark/scripts/inner_corners.py').read_bytes())
