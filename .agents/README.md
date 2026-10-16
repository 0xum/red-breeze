# Agent task map

Read [AGENTS.md](../AGENTS.md) first. This directory is contributor guidance, not
runtime configuration or a replacement for user instructions.

| Task | Start here | Relevant sources |
| --- | --- | --- |
| Unified installation, Quick Settings, lock screen, removal | [Installation](../docs/INSTALLATION.md), [architecture](../docs/ARCHITECTURE.md) | `install.py`, `tests/test_installer.py` |
| Variant installation/application and backup | [Architecture](../docs/ARCHITECTURE.md), [recovery](../docs/RESTORE_AND_TROUBLESHOOTING.md) | `light/install.py`, `dark/install.py`, both `restore.py` files |
| Palette, mouse, GTK, decorations | [Appearance](../docs/APPEARANCE.md), [customization](../docs/CUSTOMIZATION.md) | Variant `config/settings.json`, global-theme defaults, installers, Aurorae assets |
| Panels, launcher, wallpaper | [Customization](../docs/CUSTOMIZATION.md) | Variant layout/launcher/wallpaper scripts and corresponding native layouts/assets |
| Konsole and Fish | [Appearance](../docs/APPEARANCE.md#konsole) | Both `assets/konsole/`, `assets/fish/`, installer application helpers, terminal tests |
| Administrative login appearance | [Login installation](../docs/INSTALLATION.md#login-appearance), [architecture](../docs/ARCHITECTURE.md#administrative-login-integration) | Root `install.py` (`--no-login` opt-out), `tools/install-login.py`, both `install-login.py` and `scripts/login.py` files |
| Tests, hashes, archives, versions | [Development](../docs/DEVELOPMENT.md), [workflows](WORKFLOWS.md) | `tools/project.py`, both manifests/builders/test suites, root tests |
| Docs and localization | [Language policy](LANGUAGE.md) | English Markdown, `README.pt-BR.md`, authored CLI messages |
| Licensing or asset provenance | [Credits](../THIRD_PARTY.md) | Variant `THIRD_PARTY.md`, `LICENSES/`, wallpaper adaptation/generation records |

## Sources of truth

Requested behavior comes from the user. Current behavior comes from code and
configuration. Paths, dependencies, versions, and desktop state require current
inspection. Docs describe intended behavior; [migration history](../docs/MIGRATION.md)
records past events and external backups, not current-machine guarantees.

The package manifests cover variant files only. Root tooling, documentation,
`AGENTS.md`, and `.agents/` are versioned directly by Git. Build archives and
Python caches are generated outputs. See [workflows](WORKFLOWS.md) before editing
hashes or packaging.
