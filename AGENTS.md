# Repository instructions for agents

These instructions apply to the repository and both standalone packages. Follow
explicit user instructions and preserve existing local work.

## Start with the task map

1. Establish the checkout root and inspect `git status --short`.
2. Read [.agents/README.md](.agents/README.md) and only the documentation relevant
   to the task. Do not assume this checkout has the source workstation's paths,
   dependencies, backups, or session state.
3. Follow [.agents/LANGUAGE.md](.agents/LANGUAGE.md): English is the default for
   repository artifacts; pt-BR translations are optional. Reply to users in their
   preferred language.
4. Use [.agents/WORKFLOWS.md](.agents/WORKFLOWS.md) for validation and packaging.

## Repository boundaries

- There is one root Git repository. `light/` and `dark/` are independent packages,
  not nested repositories or submodules.
- Use Python 3.9+ standard-library tooling. Do not add dependencies without a
  concrete need. KDE application helpers require the destination user's session.
- Make source changes in the repository. Installed copies under XDG directories
  are not the source of truth.
- Keep shared assets, terminal profiles, and identical login helpers synchronized.
  Each variant must remain installable without the other or root tooling.
- Preserve IDs, configuration keys, license texts, attribution, and source-asset
  provenance unless the requested change requires updating them consistently.
- Inspect intentional edits before refreshing manifests. Include changed manifests
  with package sources so integrity checks remain usable.

## Side effects and completion

- Tests and source checks use temporary destinations. Do not apply themes, replace
  panels, remove live resources, or install administrative login services as a
  routine validation step. Do those operations when the user authorizes them.
- `--layout` replaces panels. User removal and administrative login recovery are
  separate operations. Preserve backups and unrelated user settings.
- Do not commit, push, publish, or rewrite history by routine. Follow the user's
  authorization for the current work.
- Review the diff and run checks appropriate to the change. Report actual results,
  skipped coverage, and material limitations; old documentation is not current
  validation evidence.
- Update the task map when entry points or maintenance commands change. Keep
  instructions short and link to maintained docs instead of duplicating them.
