# SPDX-License-Identifier: GPL-3.0-only
import configparser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import install
import restore

ROOT = Path(__file__).resolve().parents[1]


class TerminalTests(unittest.TestCase):
    def test_native_profile_sync_resolves_both_profiles(self):
        settings = json.loads((ROOT / 'config/settings.json').read_text())['konsolerc']
        self.assertEqual(settings['LightDarkTheme']['SyncProfileWithSystemTheme'], 'true')
        for variant in ('Light', 'Dark'):
            profile = configparser.ConfigParser(interpolation=None)
            profile.read(ROOT / f'assets/konsole/PapirusBreeze{variant}.profile')
            self.assertEqual(profile['General']['Name'], settings['LightDarkTheme'][variant+'ThemeProfile'])
            self.assertEqual(profile['General']['Command'], 'fish')
            palette = configparser.ConfigParser(interpolation=None)
            palette.read(ROOT / ('assets/konsole/'+profile['Appearance']['ColorScheme']+'.colorscheme'))
            self.assertEqual(palette['General']['Opacity'], '1')
            def luminance(section):
                values=[int(v)/255 for v in palette[section]['Color'].split(',')]
                values=[v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
                return sum(v*w for v,w in zip(values,(.2126,.7152,.0722)))
            bg,fg = luminance('Background'),luminance('Foreground')
            self.assertGreater((max(bg,fg)+.05)/(min(bg,fg)+.05), 10)
            self.assertEqual(bg > fg, variant == 'Light')
        self.assertTrue((ROOT/'assets/konsole'/settings['Desktop Entry']['DefaultProfile']).exists())

    def test_fish_preserves_startup_is_idempotent_and_restores(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            config=base/'config'
            startup=config/'fish/config.fish'
            startup.parent.mkdir(parents=True)
            original='source /usr/share/example/config.fish\nset -gx MY_SETTING original\n'
            startup.write_text(original)
            backup=install.Backup(base/'state')
            install.configure_fish(config,backup)
            installed=startup.read_text()
            install.configure_fish(config,backup)
            self.assertEqual(startup.read_text(),installed)
            self.assertIn(original,installed)
            self.assertTrue(installed.index('source "$__fish_config_dir') > installed.index('MY_SETTING'))
            self.assertEqual(installed.count('# BEGIN Papirus Breeze'),1)
            restore.restore(backup.path)
            self.assertEqual(startup.read_text(),original)
            self.assertFalse((config/'fish/papirus-breeze.fish').exists())

    @unittest.skipUnless(shutil.which('fish'), 'fish não instalado')
    def test_fish_greeting_is_three_lines_and_no_fastfetch(self):
        helper=ROOT/'assets/fish/papirus-breeze.fish'
        subprocess.run(['fish','--no-config','-n',str(helper)],check=True)
        result=subprocess.run(['fish','--no-config','-c',f'source "{helper}"; fish_greeting'],
                              check=True,capture_output=True,text=True)
        plain=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',result.stdout)
        lines=[line.strip() for line in plain.splitlines() if line.strip()]
        self.assertEqual(len(lines),3)
        self.assertIn('Linux ',lines[1])
        self.assertIn('fish ',lines[2])
        self.assertNotIn('fastfetch',helper.read_text())
