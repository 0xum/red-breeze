#!/usr/bin/env python3
"""Restore an installer's complete file snapshots; close Plasma first for user backups."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import json
from pathlib import Path
import shutil
import sys


def restore(backup, dry_run=False):
    entries = json.loads((backup / "restore.json").read_text())
    for entry in reversed(entries):
        target = Path(entry["target"])
        source = backup / entry["backup"]
        if not target.is_absolute() or target == Path("/"):
            raise ValueError("Destino de backup inválido")
        if entry["existed"] and not (source.exists() or source.is_symlink()):
            raise ValueError(f"Backup incompleto: {source}")
    for entry in reversed(entries):
        target, source = Path(entry["target"]), backup / entry["backup"]
        print(("Restaurar: " if entry["existed"] else "Remover criado na instalação: ") + str(target))
        if dry_run:
            continue
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)
        if entry["existed"]:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                target.symlink_to(source.readlink(), target_is_directory=source.is_dir())
            elif source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                shutil.copy2(source, target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backup", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        restore(args.backup.resolve(), args.dry_run)
    except (OSError, ValueError, KeyError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        sys.exit(1)
