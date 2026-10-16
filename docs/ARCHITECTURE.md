# Architecture and configuration

## One repository, two standalone packages

The root contains the unified installer, shared documentation, maintenance tools,
and tests. `light/` and `dark/` are self-contained packages with their own assets,
installers, tests, manifests, and archive builders. They are not submodules or
nested Git repositories.

Global-theme IDs differ so variants coexist. `PapirusBreezeRed`, the logical
launcher name, and Konsole profile names are shared. Common assets are duplicated
intentionally; keep corresponding copies synchronized.

| Path | Responsibility |
| --- | --- |
| `install.py` | Unified menu/CLI, installation, Quick Settings registration, removal |
| `tests/test_installer.py` | Unified installation/update/removal and preservation checks |
| `tools/project.py` | Manifest updates, integrity checks, tests, standalone/complete archives |
| `tools/install-login.py` | Coordinate both administrative login profiles |
| `AGENTS.md`, `.agents/` | Contributor instructions, task routing, workflows, language policy |
| `README.pt-BR.md` | Optional Brazilian Portuguese quick-start guide |

Within each variant:

| Path | Responsibility |
| --- | --- |
| `assets/plasma/look-and-feel/<ID>/` | Metadata, defaults, colors, preview, native layout |
| `assets/plasma/desktoptheme/PapirusBreezeRed/` | Red sprites with Breeze surface inheritance |
| `assets/icons/PapirusBreezeLight/` or `PapirusBreezeDark/` | Folder/system/Dolphin/launcher overlay |
| `assets/color-schemes/` | Variant palette |
| `assets/aurorae/themes/` | Amy window decoration |
| `assets/wallpapers/` | Adaptive wallpaper, metadata, provenance |
| `assets/konsole/`, `assets/fish/` | Both terminal profiles/palettes and Fish helper |
| `config/settings.json` | Portable appearance keys applied through KConfig |
| `scripts/layout.js` | Optional panel reconstruction |
| `scripts/launcher.js`, `scripts/wallpaper.js` | Existing-launcher and wallpaper updates |
| `scripts/red_icons.py` | Source SVG transformations |
| `install.py` | Variant installation/application, `asset_paths()`, backup/copy helpers |
| `install-login.py`, `scripts/login.py` | Administrative greeter appearance and optional following |
| `restore.py` | Restore complete file snapshots |
| `manifest.json` | Version metadata and distributed-file SHA-256 hashes |
| `build.py`, `tests/` | Standalone archive and package checks |
| `LICENSES/`, `THIRD_PARTY.md` | License texts and credits |

## Unified installation and removal

The root installer loads variant modules under separate names and reuses
`asset_paths()`, `Backup`, `copy_asset()`, and `apply_profile()`. It registers the
Light/Dark pair with KConfig 6 tools. Its record is
`$XDG_STATE_HOME/papirus-breeze/installation.json`, defaulting to
`~/.local/state/papirus-breeze/installation.json`.

The record retains the original Quick Settings pair across updates and stores
fingerprints of installed resources. Installation/removal failures restore file
snapshots from that operation. Normal removal changes only owned configuration
references rather than restoring entire user configuration files. It validates
managed paths, preserves modified asset directories, and retains backups.

Before removing an active theme, live removal applies the matching native Breeze
variant. Alternate destinations require data/config/state together and do not
execute live-session appearance commands. User removal excludes administrative
login installation and external dependencies.

Unified installation configures the lock screen's native image plugin and an
adaptive wallpaper without changing daemon/security settings. It then requests
Polkit authentication to install both fixed greeter profiles and the watcher;
`--no-login`, dry runs, and alternate destinations skip administrative execution.
An authentication failure is reported separately from the successful user install.
The watched source follows the actual XDG configuration path, is ownership-checked,
and does not accept symlinks.

## Configuration changed by application

| File / state | Effect |
| --- | --- |
| `kdeglobals` | Palette, accent, icons, font, Qt style, global theme, animation/contrast |
| `kwinrc` | Aurorae decoration/buttons and Breeze window switcher |
| `plasmarc` | `PapirusBreezeRed` style |
| `kcminputrc` | Mouse theme and size |
| `auroraerc`, `ksplashrc` | Decoration button size and Breeze splash |
| `kscreenlockerrc` | Target-system adaptive wallpaper URI |
| `konsolerc` | Light/Dark profiles, synchronization, default profile |
| `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` | Light/dark preference, theme, icons, font, cursor, integration |
| `fish/config.fish` | Managed interactive-source block after existing configuration |
| `fish/papirus-breeze.fish` | Compact greeting, colors, Pure settings |
| Plasma Shell state | Desktop wallpaper and launcher icons; panels only with `--layout` |

KDE utilities can also synchronize GTK helper files; installers snapshot these
before applying. Konsole profiles are copied individually to retain unrelated
profiles. Global-theme defaults do not run Fish or all installer extras, so GUI
selection and a complete `--apply` have different effects.

## Integrity and packaging

Variant manifests cover files inside their own package, including docs/scripts,
but exclude the manifest itself, Git, caches, and distribution outputs. Root files
are tracked by Git rather than a variant manifest. Only refresh hashes after
intentional edits. Paths derive from XDG directories, not the source workstation.

Each `build.py` creates a self-contained standalone archive. The maintenance tool
also creates `dist/papirus-breeze-<version>.tar.gz` with both variants, the unified
installer, documentation, agent guidance, and tests. Variant tests run in separate
processes to avoid collisions between modules named `install`/`restore`.

## Export boundaries

The package does not import accounts, authentication, activities, monitor IDs,
resolutions, personal favorites, general shortcuts, default applications, Night
Color, scaling, or tiling settings. User installation does not change the login
shell or install dependencies. The splash uses native Breeze.

## Administrative login integration

The identical `scripts/login.py` helpers are distributed with both variants.
The installed runtime in `/usr/local/libexec/` runs `--sync` without importing
code from the personal repository. systemd path/service units react to changes
in the selected user's palette and select fixed administrative profiles. They do
not restart the display manager.

The service accepts known palettes, checks a regular source file owned by the
selected user, and refuses symlink configuration targets. Configuration writes
are atomic and preserve unrelated authentication/session keys. Greeter-only
caches are cleared when applying a changed palette. Assets remain accessible
outside the normal user's private home; the greeter receives the supplied icon
overlay with Breeze/hicolor fallbacks, not a copy of the full Papirus library.

The original integration was checked against KDE 6.8.0 source:
[native synchronization helper](https://github.com/KDE/plasma-login-manager/blob/v6.8.0/src/frontend/kcm/auth/plasmaloginauthhelper.cpp)
and [Breeze greeter complementary colors](https://github.com/KDE/plasma-login-manager/blob/v6.8.0/src/frontend/greeter/qml/Main.qml).
This is provenance, not a claim that every target system runs that version.
