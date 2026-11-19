# Default window decorations

Both variants use locally adapted jomada Moe 1.9 decorations: `Moe` for Light
and `MoeDark` for Dark. Their IDs, colors, layout, and upstream metadata remain
unchanged. Amy remains an alternative.

## Button behavior

The close, minimize, maximize, and restore buttons are colored circles with no
inner symbol, including hover and pressed states. The normal circle uses 85% of
its drawing area; hover uses 100%, a roughly 18% increase. Pressed artwork uses
78%. Transparent bounds keep button size and spacing fixed. The theme's native
state cross-fade is 120 ms; this is separate from the click animations below.

| Click | Animation | Window action |
| --- | --- | --- |
| Maximize / restore | Scale 1 → 0.78 → 1.18 → 0.96 → 1 over 355 ms | Immediate; the bounce runs alongside the window change |
| Minimize | Opacity 1 → 0 over 140 ms | Requested after the fade completes |
| Close | Opacity 1 → 0 over 140 ms | Requested after the fade completes |

The fade resets opacity after the request, so a restored minimized window or a
window that keeps a save-confirmation dialog has a visible button. Further clicks
on a fading button are blocked until its pending action is dispatched. This
animates the button, not the whole window. Close confirmation remains controlled
by the application. Right/middle-click maximize behavior is retained.

## Sources and installation

Each standalone package includes:

- `assets/aurorae/themes/Moe/` or `MoeDark/`: the SVG states and theme settings.
- `assets/kwin/aurorae/`: the shared KDE QML runtime, with custom click handlers.
- `LICENSES/GPL-2.0-or-later.txt`: the QML license; file notices remain intact.

The runtime copies must remain byte-identical across Light and Dark. Custom click
animations are gated on the exact names `Moe` and `MoeDark`; other Aurorae themes
retain the copied upstream behavior. This is a per-user override of the shared
Aurorae QML entry point, not a system-file patch. The captured runtime is from
KDE Aurorae 6.8.3; review it against upstream after KDE/Aurorae upgrades.

The unified installer and either standalone installer copy the runtime to
`$XDG_DATA_HOME/kwin/aurorae/` (default `~/.local/share/kwin/aurorae/`) and the SVG
themes to `$XDG_DATA_HOME/aurorae/themes/`. Existing resources enter the normal
installer backup. No manual copying from the original workstation is required.

```sh
python3 install.py install --apply dark --no-login
```

Use `light` for the other variant. Without `--apply`, installation only copies
the assets; log out and back in before evaluating newly installed QML if Aurorae
was already loaded. With `--apply`, the installer briefly selects Breeze and then
reloads Aurorae to invalidate its QML cache. It preserves panel layouts unless
`--layout` is explicitly supplied. Switching the global theme later does not
install missing assets; install the package first.

Unified removal uses the existing fingerprint checks and recovery snapshot;
locally modified resources are preserved. Standalone recovery uses its
`restore.py` and recorded backup. See [recovery](RESTORE_AND_TROUBLESHOOTING.md).
After restoring/removing the QML runtime, log out and back in to clear cached QML.

## Maintenance and validation

Edit the repository sources, synchronize the shared runtime, and refresh both
manifests with `python3 tools/project.py manifest`. Run `check`, `test`, and `build`
through the same tool. Installer tests cover copying and restoring a preexisting
runtime in temporary destinations. A graphical check on a compatible Plasma
session should include maximize/restore, close with an unsaved document, and
minimize followed by restoration. Applying a theme is a live desktop change;
isolated source and packaging tests do not perform it.
