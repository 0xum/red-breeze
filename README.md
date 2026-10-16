# Papirus Breeze

Light and Dark themes for **KDE Plasma 6**, built around Breeze, red Papirus
icons, and the **`#E93D58`** accent. Package version: **1.0.13**.

English is the default language for documentation and command-line output.
An optional [Brazilian Portuguese guide](README.pt-BR.md) is available.

![Red launcher with a transparent center](light/assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg)

| Component | Light | Dark |
| --- | --- | --- |
| Global theme | `com.delta.papirus-breeze-light` | `com.delta.papirus-breeze-dark` |
| Color scheme / icons | `PapirusBreezeLight` | `PapirusBreezeDark` |
| Qt / Plasma style | Breeze / `PapirusBreezeRed` | Breeze / `PapirusBreezeRed` |
| Window decoration | Amy Light Aurorae | Amy Papirus Dark |
| GTK | Breeze | Breeze-Dark |
| Adaptive wallpaper | Moe | MoeDark |
| Mouse pointer | Breeze Dark, 18 px | Breeze Light, 18 px |
| Konsole | White background | Dark background |

Both variants include red folders, system icons and Dolphin icons, a vector
launcher with a transparent center, and a red animated terminal cursor.
The optional layout creates one floating **32 px panel per connected monitor**,
with no pinned applications. Fish includes a compact system greeting.

## Install or remove

Requirements: Linux, KDE Plasma 6, Python 3.9+, Breeze/Aurorae, Papirus/Papirus-Dark,
and the KDE configuration tools. Fish and JetBrainsMono Nerd Font are required
for the supplied terminal profiles. See the full [installation guide](docs/INSTALLATION.md).

From the repository root or the extracted complete package, run as your normal user:

```bash
python3 install.py
```

The menu offers installation, updates, Light/Dark application, removal, and
prerequisite checks. Direct commands are also available:

```bash
python3 install.py check
python3 install.py install
python3 install.py install --apply light
python3 install.py install --apply dark
python3 install.py status
python3 install.py remove --dry-run
python3 install.py remove
```

Installation registers both variants as the Light/Dark pair in **System Settings
→ Quick Settings**. Reopen System Settings if it was already running. Without
`--apply`, installation keeps the current appearance and panel layout.
User installation and removal do not require `sudo`.

To replace the existing panels with the supplied layout:

```bash
python3 install.py install --apply light --layout
```

**`--layout` removes the current panels.** Omit it to keep their structure,
height, and pinned applications. Removal restores the previous Quick Settings
pair when available, preserves modified resources and backups, and switches an
active Papirus theme to the matching Breeze variant before deleting assets.

## Optional login appearance

Login appearance has a separate administrative installer. To install both
profiles and follow the current user's Light/Dark selection:

```bash
python3 tools/install-login.py --follow-user "$USER" --dry-run
sudo python3 tools/install-login.py --follow-user "$USER"
```

The user installer does not install or remove this administrative integration.
See [installation](docs/INSTALLATION.md#login-appearance) and
[restoration](docs/RESTORE_AND_TROUBLESHOOTING.md#restore-a-snapshot).

## Documentation

- [Installation, Quick Settings, removal, and login](docs/INSTALLATION.md)
- [Appearance, panels, icons, Konsole, and Fish](docs/APPEARANCE.md)
- [Customization](docs/CUSTOMIZATION.md)
- [Architecture and configuration files](docs/ARCHITECTURE.md)
- [Backups, restoration, and troubleshooting](docs/RESTORE_AND_TROUBLESHOOTING.md)
- [Development and distribution](docs/DEVELOPMENT.md)
- [Repository migration history](docs/MIGRATION.md)
- [Changelog](CHANGELOG.md) and [third-party credits](THIRD_PARTY.md)
- Standalone packages: [Light](light/README.md) and [Dark](dark/README.md)
- Contributor instructions: [AGENTS.md](AGENTS.md) and [.agents/README.md](.agents/README.md)

## Repository and distribution

There is one Git repository at the root. `light/` and `dark/` are ordinary
subdirectories, each with its own installer, assets, tests, and integrity manifest.
Shared assets are intentionally duplicated so each variant can be distributed alone.

```bash
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
```

The complete archive, including the unified installer, is written to `dist/`.
Standalone archives are written to `light/dist/` and `dark/dist/`.
Build outputs and Python caches are ignored by Git.

Original scripts and composition use GPL-3.0-only. Third-party assets retain
their own licenses, including CC-BY-SA-4.0 wallpapers and LGPL KDE resources.
Read [THIRD_PARTY.md](THIRD_PARTY.md) before redistribution.
