# Maintenance workflows

## Establish scope

Inspect `git status --short` and the relevant diff before editing. Preserve existing
work and distinguish the root unified `install.py` from the per-variant scripts.
Use the [task map](README.md) rather than reading every asset or subsystem.

## Source changes and manifests

After intentional changes inside either package:

```bash
python3 tools/project.py manifest
python3 tools/project.py check
```

Review sources before refreshing hashes. Do not refresh to hide unexpected
corruption. Root-only changes do not require variant manifest changes unless the
covered package contents also changed. Use `--variant light` or `--variant dark`
when the task is truly limited to one package.

Shared assets are duplicated to preserve standalone packages. Both Konsole profile
sets, Fish helpers, Plasma style assets, and login helpers must agree where shared.
Keep native panel layouts equivalent to their installation-script counterparts.
Keep pointer settings consistent across dependencies, GTK, KConfig, native defaults,
application commands, and greeter provisioning.

## Validation

Use checks appropriate to the change:

```bash
python3 tools/project.py test
python3 tools/project.py build
git diff --check
```

Tests run in temporary destinations. Read skips; root installer tests require
KConfig 6, and optional variant checks can require Node, Fish, or systemd tools.
Do not add tests that merely restate a trivial implementation. Changes to removal,
preservation, or recovery need meaningful lifecycle/failure coverage.

For unified lifecycle verification, supply all three alternate destinations:

```bash
python3 install.py install --data-dir /tmp/papirus/share --config-dir /tmp/papirus/config --state-dir /tmp/papirus/state
python3 install.py remove --data-dir /tmp/papirus/share --config-dir /tmp/papirus/config --state-dir /tmp/papirus/state
```

Use a fresh temporary root and do not reuse another user's test directories.
For language-only changes, smoke-test help/menu text and documentation links.
For packaging changes, extract the complete archive and check its installer and
manifests. Do not apply themes, use `--layout`, or modify login services merely
to validate sources; those operations need task authorization.

## Distribution and versions

`build` generates one complete archive and two standalone archives. Preserve each
package's credits, license texts, and wallpaper provenance. Keep standalone docs
usable without the root installer or docs directory. Include new root docs and
contributor entry points in the complete archive's packaging list when appropriate.

Version changes span both manifests, global-theme metadata, builder/doc references,
and version assertions. See [development](../docs/DEVELOPMENT.md#versions-and-archives).
Do not publish or tag merely because archives were built.

## Handoff

Review the final diff, report current checks and material limits, and update the
map if entry points changed. Commit or publish only when authorized. Do not store
chat transcripts or machine-specific assumptions as repository instructions.
