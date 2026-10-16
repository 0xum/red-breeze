#!/usr/bin/env python3
"""Install the complete login appearance, optionally following the user's theme."""
# SPDX-License-Identifier: GPL-3.0-only
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
from install import ROOT, Backup, copy_asset, verify_assets, write_setting
sys.path.insert(0, str(ROOT / "scripts"))
import login


def main(argv=None):
    return login.main(ROOT, argv)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
