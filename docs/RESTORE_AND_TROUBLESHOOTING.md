# Backups, restoration, and troubleshooting

## Backup locations

Each operation prints its snapshot directory. Default locations:

| Operation | Directory |
| --- | --- |
| Unified install/remove | `~/.local/state/papirus-breeze/backups/<timestamp>/` |
| Light user install | `~/.local/state/papirus-breeze-light/backups/<timestamp>/` |
| Dark user install | `~/.local/state/papirus-breeze-dark/backups/<timestamp>/` |
| Light login install | `/var/lib/papirus-breeze-light/backups/<timestamp>/` |
| Dark login install | `/var/lib/papirus-breeze-dark/backups/<timestamp>/` |

User backups respect `XDG_STATE_HOME`. `restore.json` records targets, whether they
existed, and snapshot paths. Restoration removes resources created by the original
operation. Asset directories are snapshotted as units; keep personal additions out
of these reserved directories.

## Restore a snapshot

For normal unified removal, use `python3 install.py remove`. It preserves unrelated
configuration and custom resources. Snapshot restoration is a recovery operation
that restores **whole files**, including settings changed after the snapshot.

Close the graphical Plasma session and use a TTY before restoring its configuration,
because a running session can write those files again:

```bash
python3 light/restore.py /path/to/backup --dry-run
python3 light/restore.py /path/to/backup
```

Both variant restorers accept the same format, including unified backups.
For multiple operations, restore in reverse order, newest first. Review the
`--dry-run` output before choosing snapshots.

Before restoring administrative login snapshots, disable theme following:

```bash
sudo systemctl disable --now papirus-breeze-login.path papirus-breeze-login.service
```

Restore those snapshots with `sudo`. Run `sudo systemctl daemon-reload` afterward
if unit files were restored. To undo both login-profile installations, restore
both administrative snapshots in reverse order. The user remover does not undo
this separate installation.

To change appearance rather than restore state, use
`python3 install.py install --apply light` or `--apply dark`. An installed login
watcher follows the selected Papirus palette; otherwise apply the matching static
login profile separately.

## Quick Settings does not show both variants

Run `python3 install.py status`. The keys should be:

```ini
[KDE]
DefaultLightLookAndFeel=com.delta.papirus-breeze-light
DefaultDarkLookAndFeel=com.delta.papirus-breeze-dark
```

Rerun `python3 install.py install` and reopen System Settings. Individual package
installers do not register the full pair. A removed/customized asset directory may
be preserved deliberately; inspect removal output and backups before deleting it.

## Panels changed unexpectedly

`--layout` and the GUI's **Desktop and window layout** option replace panels.
Omit them to retain panel height and pinned applications. The supplied layout
creates one floating 32 px panel per currently connected monitor. No service
creates panels when monitors are connected later.

## Folders or icons are still blue or purple

Check the active icon theme, Papirus/Papirus-Dark dependencies, and
`PapirusBreezeRed` Plasma style. The overlay includes generic folder aliases and
Dolphin icons. Running applications may cache icons; reopen them or start a new
session. Unrelated applications inherit their original base icons.

## Trash appears as a user avatar

Version 1.0.12 added explicit empty/full trash icons and symbolic aliases. Without
`user-trash` and `user-trash-full`, KDE could shorten the name to `user` and use
the avatar. Reinstall and refresh the application/session. The trash bookmark
should still use `user-trash`; personal Places entries do not need changing.

## The launcher's center looks white or black

It is a transparent cutout and shows the background beneath it. If an old solid
version remains, reinstall the SVG and refresh the session cache. Keep
`fill-rule="evenodd"` when editing the compound path.

## Konsole does not follow Light/Dark

Install both profiles, apply a variant at least once, and reopen Konsole. Check
`konsolerc`'s `LightDarkTheme` group and the exact profile display names. Older
versions may require manual profile selection; the source workstation used
Konsole 26.08.2. The red terminal cursor is separate from the mouse pointer.
Fish and the configured font are external prerequisites.

## Fish still displays Fastfetch

The managed block must come after distribution setup in `fish/config.fish` and
source the helper only in interactive sessions. Start a new Fish session. A later
`fish_greeting` definition can replace the compact greeting.

## Wallpaper does not follow the palette or login uses another image

Desktop and lock-screen settings should reference the adaptive package directory;
a manually selected single image remains fixed. Login only follows after
administrative installation with `--follow-user`. Check:

```bash
systemctl status papirus-breeze-login.path
journalctl -u papirus-breeze-login.service
```

The watched user is recorded in `/etc/papirus-breeze-login.json`; last applied
state is `/var/lib/papirus-breeze-login/current.json`. Other themes are ignored.
Both login variants must be installed. After changing login managers, reinstall
the profiles for the new account/backend.

## A hash differs or a dependency is missing

For intentional source edits, follow [customization](CUSTOMIZATION.md) and update
manifests. Otherwise recover a correct copy from Git or a distribution archive;
do not accept corrupted content by refreshing hashes. Install missing dependencies
through your distribution. Installers do not download or install them automatically.
