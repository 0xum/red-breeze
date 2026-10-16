# SPDX-License-Identifier: GPL-3.0-only
import configparser
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install
import restore


class PackageTests(unittest.TestCase):
    def test_dark_configuration_is_consistent(self):
        profile = json.loads((ROOT / "config/settings.json").read_text())
        self.assertEqual(profile["kdeglobals"]["General"]["ColorScheme"], "PapirusBreezeDark")
        self.assertEqual(profile["kdeglobals"]["General"]["AccentColor"], "233,61,88")
        self.assertEqual(profile["kcminputrc"]["Mouse"]["cursorTheme"], "breeze_cursors")
        self.assertEqual(profile["kwinrc"]["org.kde.kdecoration2"]["theme"], "__aurorae__svg__Amy-Papirus-Dark")
        package = ROOT / "assets/plasma/look-and-feel/com.delta.papirus-breeze-dark"
        metadata = json.loads((package / "metadata.json").read_text())
        self.assertEqual(metadata["KPlugin"]["Id"], install.THEME_ID)
        defaults = configparser.ConfigParser(interpolation=None)
        defaults.read(package / "contents/defaults")
        self.assertEqual(defaults["kdeglobals][General"]["ColorScheme"], "PapirusBreezeDark")

    def test_dark_palette_text_contrast(self):
        def luminance(rgb):
            values = [int(v) / 255 for v in rgb.split(",")]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
            return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))
        config = configparser.ConfigParser(interpolation=None)
        config.read(ROOT / "assets/color-schemes/PapirusBreezeDark.colors")
        for group in ("Window", "View", "Button", "Header", "Tooltip", "Selection"):
            section = config["Colors:" + group]
            a, b = sorted((luminance(section["ForegroundNormal"]), luminance(section["BackgroundNormal"])))
            self.assertGreaterEqual((b + 0.05) / (a + 0.05), 4.5, group)

    def test_native_reset_has_custom_layout_and_adaptive_moe(self):
        package = ROOT / "assets/plasma/look-and-feel/com.delta.papirus-breeze-dark"
        native_layout = package / "contents/layouts/org.kde.plasma.desktop-layout.js"
        expected = (ROOT / install.LAYOUT).read_text().replace("__WALLPAPER_URI__", '"file://" + userDataPath("data") + "/wallpapers/MoeDark"')
        self.assertEqual(native_layout.read_text(), expected)
        self.assertNotIn("__WALLPAPER_URI__", native_layout.read_text())
        self.assertEqual((package / "contents/colors").read_bytes(),
                         (ROOT / "assets/color-schemes/PapirusBreezeDark.colors").read_bytes())
        defaults = configparser.ConfigParser(interpolation=None)
        defaults.read(package / "contents/defaults")
        self.assertEqual(defaults["Wallpaper"]["Image"], "MoeDark")
        wallpaper = ROOT / "assets/wallpapers/MoeDark"
        self.assertTrue((wallpaper / "contents/images/3073x1420.png").exists())
        self.assertTrue((wallpaper / "contents/images_dark/1844x853.png").exists())
        layout = (ROOT / install.LAYOUT).read_text()
        self.assertNotIn("cachyos-wallpapers", layout)
        self.assertNotIn("north.png", layout)

    def test_manifest_and_portability(self):
        manifest = install.verify_assets()
        self.assertEqual(manifest["version"], "1.0.12")
        for path in list((ROOT / "assets").rglob("*")) + list((ROOT / "config").rglob("*")):
            if path.is_file() and path.suffix in {".json", ".colors", ".js", ".desktop", ".theme"}:
                self.assertNotIn("/home/delta", path.read_text())

    def test_dry_run_creates_no_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = install.main(["--dry-run", "--data-dir", str(base / "share"),
                                   "--config-dir", str(base / "config"), "--state-dir", str(base / "state")])
            self.assertEqual(result, 0)
            self.assertEqual(list(base.iterdir()), [])

    def test_asset_install_and_restore_preserves_existing_asset(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            data, config, state = base / "share", base / "config", base / "state"
            old = data / "wallpapers/MoeDark/custom.txt"
            old.parent.mkdir(parents=True)
            old.write_text("original")
            other_profile = data / "konsole/Existing.profile"
            other_profile.parent.mkdir(parents=True)
            other_profile.write_text("[General]\nName=Existing\n")
            self.assertEqual(install.main(["--data-dir", str(data), "--config-dir", str(config),
                                           "--state-dir", str(state)]), 0)
            self.assertTrue((data / "wallpapers/MoeDark/contents/images_dark/1844x853.png").exists())
            self.assertFalse(config.exists())
            self.assertEqual(other_profile.read_text(), "[General]\nName=Existing\n")
            self.assertTrue((data / "konsole/PapirusBreezeLight.profile").exists())
            self.assertTrue((data / "konsole/PapirusBreezeDark.profile").exists())
            backup = next((state / "papirus-breeze-dark/backups").iterdir())
            restore.restore(backup)
            self.assertEqual(old.read_text(), "original")
            self.assertFalse((data / "icons/PapirusBreezeDark").exists())

    def test_palette_and_overlay_match_export(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(ROOT / "assets/color-schemes/PapirusBreezeDark.colors")
        self.assertEqual(config["General"]["AccentColor"], "233,61,88")
        self.assertEqual(config["Colors:Window"]["BackgroundNormal"], "32,35,38")
        overlay = ROOT / "assets/icons/PapirusBreezeDark"
        self.assertEqual(len(list(overlay.rglob("*.svg"))), 22562)
        config.read(overlay / "index.theme")
        self.assertEqual(config["Icon Theme"]["Inherits"], "Papirus-Dark,breeze-dark,hicolor")
        self.assertFalse(any(p.is_symlink() for p in (ROOT / "assets").rglob("*")))

    def test_system_icons_have_fixed_red_without_recoloring_text_palette(self):
        import xml.etree.ElementTree as ET
        overlay = ROOT / "assets/icons/PapirusBreezeDark"
        for name in ("configure", "document-new", "edit-paste", "list-add"):
            svg = (overlay / "16x16/actions" / (name + ".svg")).read_text()
            self.assertIn("#E93D58", svg)
            nodes = list(ET.fromstring(svg).iter())
            self.assertFalse(any("ColorScheme-Text" in node.get("class", "").split() for node in nodes))
        style = ROOT / "assets/plasma/desktoptheme/PapirusBreezeRed"
        for name in ("notification", "device", "computer", "kdeconnect", "configure"):
            self.assertIn("#E93D58", (style / "icons" / (name + ".svg")).read_text())
        profile = json.loads((ROOT / "config/settings.json").read_text())
        self.assertEqual(profile["plasmarc"]["Theme"]["name"], "PapirusBreezeRed")
        palette = configparser.ConfigParser(interpolation=None)
        palette.read(ROOT / "assets/color-schemes/PapirusBreezeDark.colors")
        self.assertNotEqual(palette["Colors:Window"]["ForegroundNormal"], "233,61,88")

    def test_trash_aliases_do_not_fall_back_to_generic_user(self):
        import xml.etree.ElementTree as ET
        overlay = ROOT / "assets/icons/PapirusBreezeDark"
        index = configparser.ConfigParser(interpolation=None)
        index.read(overlay / "index.theme")
        directories = index["Icon Theme"]["Directories"].split(",")
        generic = ET.parse(overlay / "22x22/actions/user.svg").getroot()
        generic_paths = [node.get("d") for node in generic.iter() if node.tag.endswith("}path")]
        for size in (16, 22, 24, 32, 48, 64, 96, 128):
            directory = f"{size}x{size}/places"
            self.assertIn(directory, directories)
            for name in ("user-trash", "user-trash-full", "user-trash-symbolic", "user-trash-full-symbolic"):
                with self.subTest(size=size, name=name):
                    icon = overlay / directory / (name + ".svg")
                    self.assertTrue(icon.is_file(), "KDE can fall back from user-trash to user")
                    self.assertIn("#E93D58", icon.read_text())
                    geometry = ET.parse(icon).getroot()
                    paths = [node.get("d") for node in geometry.iter() if node.tag.endswith("}path")]
                    self.assertNotEqual(paths, generic_paths)
            self.assertNotEqual((overlay / directory / "user-trash.svg").read_bytes(),
                                (overlay / directory / "user-trash-full.svg").read_bytes())

    def test_generic_directory_aliases_use_red_folder(self):
        overlay = ROOT / "assets/icons/PapirusBreezeDark"
        index = configparser.ConfigParser(interpolation=None)
        index.read(overlay / "index.theme")
        directories = index["Icon Theme"]["Directories"].split(",")
        for size in ("22x22", "24x24", "32x32", "48x48", "64x64", "96x96", "128x128"):
            folder = overlay / size / "places/folder.svg"
            for alias in ("inode-directory.svg", "gtk-directory.svg", "stock_folder.svg"):
                self.assertEqual((folder.parent / alias).read_bytes(), folder.read_bytes(), alias)
        for path in overlay.rglob("*.svg"):
            self.assertIn(str(path.parent.relative_to(overlay)), directories)

    @unittest.skipUnless(shutil.which("kwriteconfig6"), "kwriteconfig6 não instalado")
    def test_kconfig_keeps_login_and_nested_wallpaper_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp)
            target = config / "plasmalogin.conf"
            target.write_text("[Autologin]\nSession=keep-session\n\n[General]\nNumlock=on\n")
            install.write_setting(config, target.name, "Greeter][Wallpaper][org.kde.image][General",
                                  "Image", "file:///portable/Moe.png")
            result = target.read_text()
            self.assertIn("Session=keep-session", result)
            self.assertIn("Numlock=on", result)
            self.assertIn("[Greeter][Wallpaper][org.kde.image][General]", result)
            self.assertIn("Image=file:///portable/Moe.png", result)

    def test_login_dry_run_never_copies_or_changes_config(self):
        spec = importlib.util.spec_from_file_location("install_login", ROOT / "install-login.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module.pwd, "getpwnam") as account, \
                patch.object(module.shutil, "which", return_value="/mock/kwriteconfig6"), \
                patch.object(module, "copy_asset") as copy, \
                patch.object(module, "write_setting") as write:
            account.return_value.pw_dir = "/var/lib/plasmalogin"
            self.assertEqual(module.main(["--manager", "plasma-login", "--dry-run"]), 0)
            copy.assert_not_called()
            write.assert_not_called()

    def test_apply_uses_destination_paths_and_keeps_panels(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            data, config, state = base / "share", base / "config", base / "state"
            config.mkdir()
            original = config / "kdeglobals"
            original.write_text("[General]\nBrowserApplication=keep.desktop\n")
            gtk = config / "gtk-3.0/settings.ini"
            gtk.parent.mkdir()
            gtk.write_text("[Settings]\ngtk-cursor-blink=false\n")
            backup = install.Backup(state)
            with patch.object(install.subprocess, "run") as run:
                install.apply_profile(data, config, backup)
            calls = [c.args[0] for c in run.call_args_list]
            dbus = [c for c in calls if "org.kde.PlasmaShell.evaluateScript" in c]
            self.assertEqual(len(dbus), 1)
            self.assertNotIn("panel.remove()", dbus[0][-1])
            self.assertIn('widget.writeConfig("icon", "papirus-breeze-launcher")', dbus[0][-1])
            self.assertIn((data / "wallpapers/MoeDark").as_uri(), dbus[0][-1])
            self.assertTrue(any("kscreenlockerrc" in " ".join(c) and "Greeter" in c for c in calls))
            self.assertFalse(any("BrowserApplication" in c for c in calls))
            self.assertIn("gtk-cursor-blink=false", gtk.read_text())
            self.assertIn("gtk-application-prefer-dark-theme=true", gtk.read_text())
            self.assertIn("gtk-theme-name=Breeze-Dark", gtk.read_text())
            restore.restore(backup.path)
            self.assertEqual(original.read_text(), "[General]\nBrowserApplication=keep.desktop\n")

    @unittest.skipUnless(shutil.which("node"), "node é opcional para validar scripts JS")
    def test_layout_with_one_and_two_monitors(self):
        script = (ROOT / install.LAYOUT).read_text().replace("__WALLPAPER_URI__", json.dumps("file:///test/share/wallpapers/MoeDark"))
        harness = r'''
const assert = require('assert');
const old = [{remove() { this.removed = true; }}];
let created = [];
function panels() { return old; }
function Panel() { this.widgets = []; created.push(this); }
Panel.prototype.addWidget = function (plugin) {
    let widget = {plugin, config: {}, writeConfig(k,v) {this.config[k]=v;}};
    this.widgets.push(widget); return widget;
};
let desktop = {writeConfig(k,v) {this[k]=v;}, reloadConfig() {}};
function desktops() {return [desktop];}
function userDataPath() {return '/test/share';}
let screenCount = Number(process.argv[1]);
'''
        assertions = r'''
assert(old[0].removed);
assert.equal(created.length, screenCount);
created.forEach((p, i) => {
    assert.equal(p.screen, i); assert.equal(p.height, 32);
    assert.equal(p.location, 'bottom'); assert(p.floating);
    assert.equal(p.widgets.length, 7);
    assert.equal(p.widgets[0].config.icon, "papirus-breeze-launcher");
    const tasks = p.widgets.filter(w => w.plugin === "org.kde.plasma.icontasks");
    assert.equal(tasks.length, 1);
    assert.equal(tasks[0].config.launchers, "");
});
assert.equal(desktop.Image, 'file:///test/share/wallpapers/MoeDark');
'''
        native = (ROOT / "assets/plasma/look-and-feel/com.delta.papirus-breeze-dark/contents/layouts/org.kde.plasma.desktop-layout.js").read_text()
        for count in (1, 2):
            for candidate in (script, native):
                subprocess.run(["node", "-e", harness + candidate + assertions, str(count)], check=True)


if __name__ == "__main__":
    unittest.main()
