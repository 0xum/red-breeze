# Papirus Breeze Light

A standalone KDE Plasma 6 theme package from the
[Papirus Breeze repository](https://github.com/0xum/red-breeze). Version: **1.0.13**.
English is the default language. The complete repository also provides an optional
[Brazilian Portuguese guide](https://github.com/0xum/red-breeze/blob/main/README.pt-BR.md).

Commands below run **inside this package directory**. In the complete repository,
prefix script paths with `light/`. The root `install.py` is a different,
unified installer with a menu, Quick Settings registration, and removal.

![Moe Light wallpaper](assets/wallpapers/Moe/contents/images/3073x1420.png)

## Included appearance

| Component | Setting |
| --- | --- |
| Global theme | `com.delta.papirus-breeze-light` |
| Colors / icons | `PapirusBreezeLight`, red `#E93D58` accent |
| Qt / Plasma | Breeze / `PapirusBreezeRed` |
| GTK | Breeze |
| Window decoration | Amy-Light-Aurorae-6, small buttons |
| Mouse pointer | Breeze Dark (`breeze_cursors`), dark, 18 px |
| General / GTK font | Noto Sans, 10 pt |
| KDE animation factor | `0.25` |
| Wallpaper package | `Moe`, adaptive Light/Dark images |
| Optional panels | Floating, bottom, 32 px, one per connected monitor, no pinned applications |
| Window switcher / splash | Native Breeze |

The icon overlay contains 835 folder aliases and red system/Dolphin icons. Other
icons inherit `Papirus`. The launcher is a rounded red hexagon with a
transparent circular cutout. Both Konsole profiles include JetBrainsMono Nerd Font
11 pt, a red animated block cursor, and a Fish startup command.

## Requirements

Linux, KDE Plasma 6, and Python 3.9+. Install Breeze, Aurorae, Breeze GTK,
`Papirus`, Noto Sans, Ocean sounds, and both Breeze cursor themes through
your distribution. Fish and JetBrainsMono Nerd Font are required for the terminal.
Live application needs `kwriteconfig6`, `qdbus6`, `plasma-apply-lookandfeel`,
`plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, and `plasma-apply-cursortheme`.
Checks cover base icon/cursor themes and application tools, not every optional feature.

## Install and apply

Run as your normal user in an accessible Plasma session:

```bash
python3 install.py --check
python3 install.py --apply --dry-run
python3 install.py
python3 install.py --apply
```

Without `--apply`, only assets are installed. The theme appears under **System
Settings → Colors & Themes → Global Theme**. Application also configures GTK,
wallpaper, lock screen, Konsole, Fish, and existing launcher icons while preserving
panel structure, height, and favorites. Reopen Konsole after the first application.
The scripts respect `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_STATE_HOME`.

To replace the current panels with the supplied layout:

```bash
python3 install.py --apply --layout
```

**`--layout` removes current panels.** The GUI's **Desktop and window layout**
option has the same panel-replacement intent. Without it, current panels remain.
Monitor IDs are resolved on the target system; no background service creates
panels for monitors connected later.

The wallpaper package includes original Moe Light and adapted Moe Dark images.
Referencing the package directory lets Plasma follow Light/Dark; selecting a
single image manually fixes it. Accounts, monitor IDs, resolutions, personal
favorites, general shortcuts, authentication, Night Color, scaling, and tiling
are not imported. Fish settings do not change your login shell or replace your
whole distribution configuration.

## Quick Settings and removal

This standalone installer does not register the complete Light/Dark pair or expose
the root installer's `remove` action. For that workflow, use the complete archive
or repository, then run from its root:

```bash
python3 install.py install
python3 install.py remove
```

Unified installation also requests system authentication to enable login following;
use its `--no-login` option to skip administrative setup.
Those commands are for the **root unified installer**, not this package's script.
To undo a standalone installation, use its backup restoration procedure below.

## Optional login appearance

The administrative helper supports Plasma Login Manager and SDDM/Breeze, using
native authentication UI. It installs accessible palette/icon/cursor/wallpaper
resources without restarting the display manager or changing authentication/autologin.

```bash
python3 install-login.py --dry-run
sudo python3 install-login.py
# Optional: follow a normal graphical-session user's palette.
sudo python3 install-login.py --follow-user username
```

Install both variants for Light/Dark following. From the complete repository root,
`sudo python3 tools/install-login.py --follow-user "$USER"` installs both profiles.
Use `--manager plasma-login` or `--manager sddm` to select a backend explicitly.
Unknown palettes are ignored; static installation remains selected until changed.

Before restoring administrative snapshots or returning to static appearance:

```bash
sudo systemctl disable --now papirus-breeze-login.path papirus-breeze-login.service
```

## Backups and restoration

Each operation prints its backup. User backups default to
`~/.local/state/papirus-breeze-light/backups/`; administrative login backups use
`/var/lib/papirus-breeze-light/backups/`.

```bash
python3 restore.py /path/to/backup --dry-run
python3 restore.py /path/to/backup
```

For Plasma configuration recovery, close the graphical session and use a TTY so
it does not overwrite restored files. Restoration replaces whole files, including
settings changed after the snapshot. Restore multiple snapshots newest first.
Use `sudo` for administrative backups and run `sudo systemctl daemon-reload` if
unit files were restored. User-level removal in the unified installer is separate
from administrative login recovery.

## Validate and package

```bash
python3 -m unittest discover -s tests -v
python3 build.py
```

The archive is `dist/papirus-breeze-light-1.0.13.tar.gz`. Tests use temporary
directories and do not apply themes to the live session. The manifest records
SHA-256 hashes. After intentional source edits in the complete repository, refresh
hashes with its `tools/project.py manifest` before checking/building. Keep matching
shared assets synchronized across variants; do not accept corrupted downloads by
refreshing hashes.

Read [THIRD_PARTY.md](THIRD_PARTY.md) and the files in [LICENSES](LICENSES/) before
redistribution. The standalone archive includes its own credits and legal notices.
