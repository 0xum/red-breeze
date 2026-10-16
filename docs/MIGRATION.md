# Unified repository migration

## Historical source-workstation migration

On October 16, 2026, the original local packages were reorganized:

| Previous directory under `Projects/` | Directory under the unified repository |
| --- | --- |
| `papirus-breeze-light/` | `light/` |
| `papirus-breeze-dark/` | `dark/` |

Installed assets and session configuration were independent of the checkout path.
The reorganization itself did not change the installed appearance.

The source-workstation migration record reported clean original repositories,
verified Git bundles, original Git directories, and logs under:

```text
~/.local/state/papirus-breeze/repository-backups/20261016-141813/
├── papirus-breeze-light.bundle
├── papirus-breeze-dark.bundle
├── light.git/
├── dark.git/
├── light-history.txt
├── dark-history.txt
└── migration.json
```

These are external historical backups, not files included in a clone or release.
Do not assume they exist on another machine. If you have those bundles, inspect
them before using them and clone into a new directory, for example:

```bash
git clone /path/to/papirus-breeze-light.bundle /path/to/new/light-history
```

The recorded original heads were Light `57c76d5` and Dark `8aeb91a`, both changes
to the launcher's transparent center. The initial unified import represented
visual version 1.0.11 and used separate commits for layout, Light, Dark, tooling,
and documentation. No remote was created during that original local operation;
this does not describe the current repository's remote configuration.

## Current checkout and installed copies

The project is now available at [0xum/red-breeze](https://github.com/0xum/red-breeze).
A checkout can have any directory name. Use `git rev-parse --show-toplevel`,
`git status`, and `git remote -v` to establish its current state. Do not restore
old `.git` directories inside `light/` or `dark/`.

Installers locate sources relative to their own file, so moving the checkout does
not relocate installed assets. Update local shortcuts if the checkout moves.
To adopt an installation previously made with standalone scripts, run
`python3 install.py install` from the complete repository; the unified remover
then manages its assets. See [installation and removal](INSTALLATION.md#updates-and-removal).
