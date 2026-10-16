# Development and distribution

## Repository layout

The repository has one `.git` at the root. `light/` and `dark/` are regular
subdirectories, not submodules or independent checkouts. The repository is hosted
at [0xum/red-breeze](https://github.com/0xum/red-breeze); inspect `git remote -v`
and `git status` for the current checkout rather than relying on historical notes.
Build outputs, Python caches, and external history bundles are ignored.

English is the default for documentation, comments, help, diagnostics, and new
commit descriptions. The optional [pt-BR guide](../README.pt-BR.md) links back to
the English documentation.

## Maintenance commands

The tools use Python's standard library:

```bash
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
```

| Action | Effect |
| --- | --- |
| `check` | Verify both variant manifests without applying appearance |
| `test` | Run isolated Light/Dark suites and root installer tests |
| `build` | Verify manifests; create two standalone archives and one complete archive |
| `manifest` | Recalculate hashes after intentional edits; leave versions unchanged |

For one variant, append `--variant light` or `--variant dark`. For session
prerequisites, use `python3 install.py check` or a variant's `install.py --check`.
These checks are distinct from source integrity and can require a live D-Bus
session. Building archives does not require applying a theme.

## After editing package files

```bash
python3 tools/project.py manifest
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
git diff --check
git status --short
```

Review edits before refreshing hashes: manifest updates accept local contents as
the new baseline. Include changed manifests with the corresponding sources.
Root documentation and tooling are outside the variant manifests; variant docs,
installers, and wallpaper provenance are covered by them.

Tests cover integrity, portability, install/restore, layouts, icon composition,
terminal integration, unified install/update/remove, preservation, and failure
recovery. Optional checks may be skipped when Node, Fish, systemd tools, or KConfig
6 are unavailable. Report the actual current results and skips rather than a fixed
historical test count. Tests use temporary directories; do not apply a theme,
replace panels, or install administrative login services just to run tests.

When adding/removing SVGs, review the expected counts and directories. Layout
checks must retain one panel per monitor, 32 px height, no pinned applications,
and the package launcher. Keep shared assets and both login helpers synchronized.

## Versions and archives

For a release version change, update variant `manifest.json` versions,
`KPlugin.Version` metadata, build/doc references, and version assertions together.
Keep both package versions equal for a complete archive. An unreleased edit or a
local build does not by itself imply a new published release.

Current output paths:

```text
dist/papirus-breeze-1.0.13.tar.gz
light/dist/papirus-breeze-light-1.0.13.tar.gz
dark/dist/papirus-breeze-dark-1.0.13.tar.gz
```

The complete archive includes both variants, unified installer, documentation,
and tests. Each standalone archive works without the other variant
or root files. Builders exclude Git, caches, and nested distribution outputs.
Generated archives stay out of Git; attach them to a release only when publishing
is requested. Extract and smoke-test a changed archive builder before distribution.

## Commits and publishing

Use a concise English description of the final change, for example:

```text
feat(installer): register the Light and Dark Quick Settings pair
fix(cursor): use contrasting pointers in both themes
docs: document installation and recovery
```

Inspect the complete diff, preserve existing local work, and include updated
manifests. Commit, push, or publish only when requested. Adding a checkout to
GitHub Desktop does not require a new repository: add the existing root and keep
both variants inside it. See [migration history](MIGRATION.md) for the original
source-workstation reorganization.
