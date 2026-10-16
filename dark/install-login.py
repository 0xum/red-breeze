#!/usr/bin/env python3
"""Configure Moe Dark for Plasma Login Manager, or optionally a Breeze-based SDDM."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys

from install import ROOT, Backup, copy_asset, verify_assets, write_setting


def detect_manager():
    service = Path("/etc/systemd/system/display-manager.service").resolve().name
    if service == "plasmalogin.service":
        return "plasma-login"
    if service == "sddm.service":
        return "sddm"
    raise RuntimeError("Gerenciador não identificado. Selecione --manager plasma-login ou --manager sddm.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manager", choices=["auto", "plasma-login", "sddm"], default="auto")
    parser.add_argument("--dry-run", action="store_true", help="mostra as ações sem exigir root nem gravar")
    args = parser.parse_args(argv)
    verify_assets()
    manager = detect_manager() if args.manager == "auto" else args.manager
    if not shutil.which("kwriteconfig6"):
        raise RuntimeError("Comando necessário: kwriteconfig6")
    if manager == "plasma-login":
        account = pwd.getpwnam("plasmalogin")
        dest = Path(account.pw_dir) / "wallpapers/MoeDark"
        config = Path("/etc/plasmalogin.conf")
        print(f"Plasma Login Manager: copiar Moe Dark para {dest}")
        print(f"Alterar apenas a referência de wallpaper em {config}")
    else:
        breeze = Path("/usr/share/sddm/themes/breeze")
        if not (breeze / "Main.qml").exists():
            raise RuntimeError("Instale o tema Breeze para SDDM antes de continuar.")
        dest = Path("/usr/local/share/wallpapers/MoeDark")
        theme = Path("/usr/share/sddm/themes/papirus-breeze-dark")
        config = Path("/etc/sddm.conf.d/90-papirus-breeze-dark.conf")
        print(f"SDDM: copiar Moe Dark para {dest}; criar variante Breeze em {theme}")
        print(f"Selecionar tema em {config}")
    print("Nenhum serviço será reiniciado ou habilitado.")
    if args.dry_run:
        return 0
    if os.geteuid() != 0:
        raise RuntimeError("Execute este comando com sudo para configurar o login do sistema.")
    backup = Backup(Path("/var/lib"))
    try:
        copy_asset(ROOT / "assets/wallpapers/MoeDark", dest, backup)
        backup.save(config)
        config.parent.mkdir(parents=True, exist_ok=True)
        image = dest / "contents/images_dark/1844x853.png"
        if manager == "plasma-login":
            # The dedicated greeter account must be able to read its wallpaper.
            for path in [dest] + list(dest.rglob("*")):
                os.chown(path, account.pw_uid, account.pw_gid)
            write_setting(config.parent, config.name,
                          "Greeter][Wallpaper][org.kde.image][General", "Image", image.as_uri())
        else:
            copy_asset(breeze, theme, backup)
            # This is a new copy; edits are included in the backed-up theme tree.
            write_setting(theme, "theme.conf.user", "General", "background", str(image))
            write_setting(theme, "theme.conf.user", "General", "type", "image")
            write_setting(theme, "theme.conf.user", "General", "showlogo", "hidden")
            write_setting(theme, "theme.conf.user", "General", "showClock", "true")
            write_setting(config.parent, config.name, "Theme", "Current", "papirus-breeze-dark")
            write_setting(config.parent, config.name, "Theme", "CursorTheme", "breeze_cursors")
            write_setting(config.parent, config.name, "Theme", "CursorSize", "18")
    finally:
        if backup.path.exists():
            print("Backup:", backup.path)
    print("Wallpaper de login configurado. Será usado na próxima tela de login.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, KeyError, subprocess.CalledProcessError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        sys.exit(1)
