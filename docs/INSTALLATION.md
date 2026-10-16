# Installation

Commands in this guide run from the repository root or the extracted complete
archive. Use the standalone instructions near the end for an individual package.
English is the default language. An optional [pt-BR guide](../README.pt-BR.md) is available.

## Requirements

- Linux, KDE Plasma 6, and Python 3.9 or later.
- Breeze for Qt/Plasma, Aurorae support, and Breeze/Breeze-Dark GTK themes.
- Papirus and Papirus-Dark icons; `Breeze_Light` and `breeze_cursors` mouse themes.
- Noto Sans and Ocean sounds. Fish and JetBrainsMono Nerd Font are needed for the supplied Konsole profiles.
- `kreadconfig6` and `kwriteconfig6` for unified installation and registration.
- For live application/removal: `qdbus6`, `plasma-apply-lookandfeel`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, and `plasma-apply-cursortheme`.
- A Konsole version with native Light/Dark profile synchronization, or manual profile selection on older versions. The source workstation used Konsole 26.08.2.
- For optional login appearance: Plasma Login Manager, or SDDM with its Breeze theme installed.

Install dependencies through your distribution's package manager. The installers
do not download software or invoke a package manager. Checks cover base
icon/cursor themes and KDE tools; they do not verify every font, GTK theme, or
optional terminal feature. Live application and removal require the destination
user's accessible Plasma session on D-Bus.

## Unified installer

Download the full repository or extract `papirus-breeze-1.0.13.tar.gz`. Run as your
normal user, without `sudo`:

```bash
python3 install.py
```

The menu offers installation/updates, Light/Dark application, removal, and checks.
Equivalent direct commands are:

```bash
python3 install.py check
python3 install.py install --dry-run
python3 install.py install
python3 install.py install --apply light
python3 install.py install --apply dark
python3 install.py status
python3 install.py remove --dry-run
python3 install.py remove
```

`install` copies both variants and registers `DefaultLightLookAndFeel` and
`DefaultDarkLookAndFeel` under `[KDE]` in `kdeglobals`. These are the
[official Plasma Quick Settings keys](https://github.com/KDE/plasma-desktop/blob/v6.7.5/kcms/landingpage/landingpage_kdeglobalssettings.kcfg).
Reopen **System Settings → Quick Settings** to see the pair if the window was
already open. Registration does not enable automatic switching by time of day.

Without `--apply`, installation keeps the current appearance and panels.
`--apply light` or `--apply dark` also sets the palette, window decoration, font,
mouse cursor, Plasma style, GTK integration, wallpaper, lock screen, Konsole,
Fish, and existing launcher icons. Reopen Konsole after the first application.
Other running applications may need to be reopened or a new graphical session.

To replace panels with the supplied layout:

```bash
python3 install.py install --apply light --layout
```

**`--layout` removes the current panels.** It creates a floating 32 px panel on
each currently connected monitor, with no pinned applications. Without it,
panel structure, height, and favorites are preserved. Connecting another monitor
later does not automatically create a new panel through this package.

## Updates and removal

Rerun `install` to update both variants. Dedicated asset directories are replaced
with backups, and the original Quick Settings selection is retained across updates.
Keep custom source changes in the repository rather than inside installed asset directories.

`remove` switches an active Papirus global theme to the matching Breeze variant
before deleting resources. It restores the previous Quick Settings pair if the
previous themes remain installed; otherwise it uses Breeze/Breeze Dark. Later
user changes to those keys are preserved. Removal also clears package references
in Konsole and lock-screen settings and removes the managed Fish startup block.

Modified asset directories, unrelated profiles, panel layouts, dependencies, and
backups are preserved. Preserved custom resources are reported and may remain in
the list of available themes. The installation record is removed when removal
completes; preserved resources can then be reviewed manually.

To adopt a legacy installation made with the per-variant scripts, run
`python3 install.py install` once. The unified remover then manages those Papirus
assets; their previous contents remain in the installation backup.

The user remover does not undo administrative login integration. See
[login appearance](#login-appearance) and
[snapshot restoration](RESTORE_AND_TROUBLESHOOTING.md#restore-a-snapshot).

## Isolated destinations

The installer respects `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_STATE_HOME`.
For a test installation, supply all three alternate directories together:

```bash
python3 install.py install --data-dir /tmp/papirus/share --config-dir /tmp/papirus/config --state-dir /tmp/papirus/state
python3 install.py remove --data-dir /tmp/papirus/share --config-dir /tmp/papirus/config --state-dir /tmp/papirus/state
```

Alternate destinations disable live application/removal actions. `--apply` cannot
be combined with them. Dependency checks can still find base icons installed in
the real user's data directory. `--dry-run` does not write files.

## Standalone packages

The individual archives remain installable without the unified installer.
From the complete repository:

```bash
python3 light/install.py --check
python3 light/install.py --apply --dry-run
python3 light/install.py
python3 dark/install.py
python3 light/install.py --apply
# Or: python3 dark/install.py --apply
```

From an extracted standalone archive, run `python3 install.py` or
`python3 install.py --apply` inside that package. The individual installer copies
assets without applying appearance unless `--apply` is supplied. It does not
register both Quick Settings choices or provide the unified `remove` command.
Each package includes both Konsole profiles. Selecting the global theme in the
GUI applies its defaults; use `--apply` at least once for the extra GTK/Fish/Konsole
configuration. Selecting **Desktop and window layout** replaces panels just like
`--apply --layout`.

## Login appearance

Login appearance runs under another account and requires an initial administrative
installation. The helper detects Plasma Login Manager or SDDM/Breeze. The source
workstation used Plasma Login Manager 6.8.0; verify your installed backend rather
than assuming the source version matches your system.

To install both profiles and follow the normal user's Light/Dark theme:

```bash
python3 tools/install-login.py --follow-user "$USER" --dry-run
sudo python3 tools/install-login.py --follow-user "$USER"
```

Pass the graphical session's normal user, not `root`. A caller can also use
Polkit through `pkexec`. The watcher reads the selected user's `kdeglobals` and
applies only the known `PapirusBreezeLight`/`PapirusBreezeDark` profiles. Other
themes are ignored. Both administrative profiles must be installed to switch.

The installer writes:

- Icons and Plasma style resources into the `plasmalogin` or `sddm` account's data directory.
- Wallpapers and fixed profiles in `/usr/local/share/papirus-breeze-login/`.
- Greeter-only `PapirusBreezeLoginLight/Dark` palettes, with complementary colors matching window colors.
- The administrative runtime at `/usr/local/libexec/papirus-breeze-login.py`.
- `/etc/papirus-breeze-login.json`, identifying the user, source path, and backend.
- `papirus-breeze-login.path` and `.service` systemd units.

The watcher selects fixed administrative profiles from a palette name. It does
not copy the user's entire `kdeglobals`, execute scripts from the user's home,
restart the display manager, or change authentication/autologin. Applied state is
stored in `/var/lib/papirus-breeze-login/current.json`; unrelated config writes do
not repeatedly apply the same palette. The result appears on the next login screen.

For a static appearance without following a user:

```bash
python3 light/install-login.py --dry-run
sudo python3 light/install-login.py
# Or: sudo python3 dark/install-login.py
```

Specify `--manager plasma-login` or `--manager sddm` to select the backend.
Standalone packages can use their own `install-login.py --follow-user username`;
install both variants with that option. SDDM uses dedicated Breeze-derived themes
and `/etc/sddm.conf`; Plasma Login Manager uses appearance keys in `/etc/plasmalogin.conf`.

If following is already enabled, disable it before returning to static selection
or restoring administrative snapshots:

```bash
sudo systemctl disable --now papirus-breeze-login.path papirus-breeze-login.service
```

Do not log out just to run installation. For administrative removal/recovery,
follow the [restoration procedure](RESTORE_AND_TROUBLESHOOTING.md#restore-a-snapshot).
