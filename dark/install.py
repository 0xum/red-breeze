#!/usr/bin/env python3
"""Install the exported theme; --apply enables it in a running Plasma 6 session."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import configparser
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
THEME_ID = "com.delta.papirus-breeze-dark"
LAYOUT = Path("scripts/layout.js")


def verify_assets():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for relative, expected in manifest["sha256"].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"Arquivo ausente ou modificado: {relative}")
    return manifest


def data_roots(data):
    return [data, Path.home() / ".icons"] + [
        Path(p) for p in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":") if p
    ]


def dependency_errors(data, applying=False):
    errors = []
    roots = data_roots(data)
    for name in ("Papirus-Dark", "breeze_cursors"):
        if not any((p / "icons" / name / "index.theme").exists() or
                   (p.name == ".icons" and (p / name / "index.theme").exists()) for p in roots):
            errors.append(f"Tema de ícones/cursor ausente: {name}")
    if applying:
        for cmd in ("kwriteconfig6", "plasma-apply-lookandfeel", "plasma-apply-colorscheme",
                    "plasma-apply-desktoptheme", "plasma-apply-cursortheme", "qdbus6"):
            if not shutil.which(cmd):
                errors.append(f"Comando ausente: {cmd}")
        if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
            errors.append("Execute --apply dentro da sessão Plasma 6 do usuário de destino.")
        elif shutil.which("qdbus6"):
            result = subprocess.run(["qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                                     "org.freedesktop.DBus.Peer.Ping"], capture_output=True, text=True)
            if result.returncode:
                errors.append("O Plasma Shell não está acessível na sessão D-Bus atual.")
    return errors


class Backup:
    def __init__(self, state):
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self.path = state / "papirus-breeze-dark/backups" / stamp
        self.entries = []
        self.seen = set()

    def save(self, target):
        target = target.absolute()
        if str(target) in self.seen:
            return
        self.seen.add(str(target))
        exists = target.exists() or target.is_symlink()
        entry = {"target": str(target), "existed": exists, "backup": str(len(self.entries))}
        self.path.mkdir(parents=True, exist_ok=True, mode=0o700)
        if exists:
            dest = self.path / entry["backup"]
            if target.is_symlink():
                dest.symlink_to(os.readlink(target), target_is_directory=target.is_dir())
            elif target.is_dir():
                shutil.copytree(target, dest, symlinks=True)
            else:
                shutil.copy2(target, dest)
        self.entries.append(entry)
        (self.path / "restore.json").write_text(json.dumps(self.entries, indent=2) + "\n")


def copy_asset(source, target, backup):
    backup.save(target)
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def write_setting(config, filename, group, key, value):
    command = ["kwriteconfig6", "--file", str(config / filename)]
    # JSON group names use KConfig's nested-group spelling, e.g. Greeter][Wallpaper.
    for part in group.split("]["):
        command += ["--group", part]
    subprocess.run(command + ["--key", key, str(value)], check=True)


def write_gtk(path, backup):
    backup.save(path)
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    config.read(path)
    if not config.has_section("Settings"):
        config.add_section("Settings")
    for key, value in {
        "gtk-application-prefer-dark-theme": "true", "gtk-theme-name": "Breeze-Dark",
        "gtk-icon-theme-name": "PapirusBreezeDark", "gtk-font-name": "Noto Sans 10",
        "gtk-cursor-theme-name": "breeze_cursors", "gtk-cursor-theme-size": "18",
        "gtk-decoration-layout": "icon:minimize,maximize,close", "gtk-enable-animations": "true",
        "gtk-sound-theme-name": "ocean",
    }.items():
        config.set("Settings", key, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        config.write(stream, space_around_delimiters=False)


def configure_fish(config, backup):
    """Source our interactive settings after distribution config without replacing it."""
    target = config / "fish/papirus-breeze.fish"
    copy_asset(ROOT / "assets/fish/papirus-breeze.fish", target, backup)
    startup = config / "fish/config.fish"
    backup.save(startup)
    existing = startup.read_text() if startup.exists() else ""
    begin = "# BEGIN Papirus Breeze terminal settings"
    end = "# END Papirus Breeze terminal settings"
    if begin in existing:
        before, managed = existing.split(begin, 1)
        if end not in managed:
            raise RuntimeError("Bloco Papirus Breeze incompleto em fish/config.fish")
        existing = before + managed.split(end, 1)[1]
    block = (begin + '\n'
             'if status is-interactive\n'
             '    source "$__fish_config_dir/papirus-breeze.fish"\n'
             'end\n' + end + '\n')
    startup.write_text(existing.rstrip("\n") + ("\n\n" if existing.strip() else "") + block)


def evaluate(script):
    subprocess.run(["qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                    "org.kde.PlasmaShell.evaluateScript", script], check=True)


def apply_profile(data, config, backup, layout=False):
    settings = json.loads((ROOT / "config/settings.json").read_text())
    wallpaper = (data / "wallpapers/MoeDark").as_uri()
    settings["kscreenlockerrc"] = {"Greeter][Wallpaper][org.kde.image][General": {
        "Image": wallpaper, "PreviewImage": wallpaper,
    }}
    # Snapshot before any KDE utility changes a file.
    for name in set(settings) | {"plasma-org.kde.plasma.desktop-appletsrc", "plasmashellrc", "kdedefaults"}:
        backup.save(config / name)
    subprocess.run(["plasma-apply-lookandfeel", "--apply", THEME_ID], check=True)
    subprocess.run(["plasma-apply-colorscheme", "PapirusBreezeDark"], check=True)
    subprocess.run(["plasma-apply-desktoptheme", "PapirusBreezeRed"], check=True)
    subprocess.run(["plasma-apply-cursortheme", "--size", "18", "breeze_cursors"], check=True)
    for filename, groups in settings.items():
        for group, values in groups.items():
            for key, value in values.items():
                write_setting(config, filename, group, key, value)
    for version in ("gtk-3.0", "gtk-4.0"):
        write_gtk(config / version / "settings.ini", backup)
    configure_fish(config, backup)
    # GTK2 files can also be rewritten by KDE's synchronization helper.
    if layout:
        script = (ROOT / LAYOUT).read_text()
        script = script.replace("__WALLPAPER_URI__", json.dumps(wallpaper))
        evaluate(script)
    appearance_script = (ROOT / "scripts/wallpaper.js").read_text().replace("__WALLPAPER_URI__", json.dumps(wallpaper))
    evaluate(appearance_script + "\n" + (ROOT / "scripts/launcher.js").read_text())
    subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"], check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="aplica o perfil na sessão Plasma 6 atual")
    parser.add_argument("--layout", action="store_true", help="com --apply, substitui painéis por um painel por monitor")
    parser.add_argument("--check", action="store_true", help="verifica integridade e dependências sem instalar")
    parser.add_argument("--dry-run", action="store_true", help="mostra ações sem gravar nem aplicar")
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))))
    parser.add_argument("--config-dir", type=Path, default=Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))))
    parser.add_argument("--state-dir", type=Path, default=Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))))
    args = parser.parse_args(argv)
    if args.layout and not args.apply:
        parser.error("--layout exige --apply")
    raw_args = argv if argv is not None else sys.argv[1:]
    if args.apply and any(arg.split("=", 1)[0] in ("--data-dir", "--config-dir", "--state-dir") for arg in raw_args):
        parser.error("diretórios alternativos são permitidos apenas para instalação de arquivos")
    data, config, state = (p.expanduser().resolve() for p in (args.data_dir, args.config_dir, args.state_dir))
    verify_assets()
    errors = dependency_errors(data, args.apply or args.check)
    print("Integridade dos arquivos: OK")
    for error in errors:
        print("Dependência:", error)
    if args.check:
        return 1 if errors else 0
    if errors and args.apply and not args.dry_run:
        return 1
    assets = [Path("plasma/desktoptheme/PapirusBreezeRed"), Path("wallpapers/MoeDark"), Path("aurorae/themes/Amy-Papirus-Dark"),
              Path("icons/PapirusBreezeDark"), Path("color-schemes/PapirusBreezeDark.colors"),
              Path("plasma/look-and-feel") / THEME_ID]
    assets += [Path("konsole") / path.name for path in sorted((ROOT / "assets/konsole").iterdir()) if path.is_file()]
    for relative in assets:
        print(f"Instalar: {data / relative}")
    if args.apply:
        print("Aplicar: cores, decoração, fonte, cursor, GTK, wallpaper, bloqueio, Konsole e Fish.")
        print("Painéis:", "substituir por um painel de 32 px por monitor" if args.layout else "preservar")
    if args.dry_run:
        print("Simulação concluída. Nenhum arquivo alterado.")
        return 0
    if os.geteuid() == 0:
        raise RuntimeError("Execute install.py como usuário normal; use install-login.py para o login.")
    backup = Backup(state)
    try:
        for relative in assets:
            copy_asset(ROOT / "assets" / relative, data / relative, backup)
        if args.apply:
            # Back up additional files potentially touched by KDE's GTK synchronizer.
            for name in ("gtkrc", "gtkrc-2.0", "gtk-3.0/settings.ini", "gtk-4.0/settings.ini", "xsettingsd/xsettingsd.conf"):
                backup.save(config / name)
            apply_profile(data, config, backup, args.layout)
    finally:
        if backup.path.exists():
            print("Backup:", backup.path)
    print("Tema instalado." if not args.apply else "Tema aplicado. Encerre e inicie a sessão para atualizar todos os aplicativos.")
    print("O login é configurado separadamente com install-login.py.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        sys.exit(1)
