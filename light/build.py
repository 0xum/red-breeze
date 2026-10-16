#!/usr/bin/env python3
"""Create dist/papirus-breeze-light-1.0.11.tar.gz without git or private backups."""
# SPDX-License-Identifier: GPL-3.0-only
import tarfile
from install import ROOT, verify_assets

if __name__ == "__main__":
    manifest = verify_assets()
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    name = "papirus-breeze-light-" + manifest["version"]
    archive = dist / (name + ".tar.gz")
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(ROOT.rglob("*")):
            relative = path.relative_to(ROOT)
            if any(p in {".git", "dist", "__pycache__"} for p in relative.parts) or path.suffix == ".pyc":
                continue
            if path.is_file():
                tar.add(path, arcname=name + "/" + str(relative), recursive=False)
    print(archive)
