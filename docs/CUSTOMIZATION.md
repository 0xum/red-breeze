# Customization

Edit repository sources and reinstall. Files under `~/.local/share/` are installed
copies; editing only those copies does not update future distributions.
When a change applies to both variants, update both. Shared assets are duplicated
intentionally to keep standalone packages self-contained.

## Launcher SVG

Sources:

- `light/assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg`
- `dark/assets/icons/PapirusBreezeDark/scalable/apps/papirus-breeze-launcher.svg`

The SVG has `viewBox="0 0 128 128"`. The `hexagon` path combines the outer contour
with a circular cutout. `fill="#E93D58"` sets its color; `Q` curves round its corners.
The second path segment describes the transparent circle centered at `(64,64)`:

```text
M 89 64 A 25 25 0 1 0 39 64 A 25 25 0 1 0 89 64 Z
```

For a radius of 20, replace that segment with:

```text
M 84 64 A 20 20 0 1 0 44 64 A 20 20 0 1 0 84 64 Z
```

Keep `fill-rule="evenodd"`. A `fill="none"` circle above a filled hexagon does not
cut through the underlying shape. Edit the compound path directly in a vector
editor. The asset needs no bitmap, filter, or renderer-specific mask.

## Palette and icons

Each variant has `assets/color-schemes/PapirusBreezeLight.colors` or its Dark
equivalent. Keep the global theme's `contents/colors` copy byte-identical to that
palette, as required by the tests.

The accent is also stored in `config/settings.json`. System icons and Plasma
sprites use fixed red values, so changing `AccentColor` alone does not recolor
them. For a complete color change, also review both icon overlays,
`assets/plasma/desktoptheme/PapirusBreezeRed/`, the launcher SVG, and Konsole assets.

`scripts/red_icons.py` records the SVG transformations. The installer uses the
included final SVGs and does not run this generator. Preserve authorship,
licenses, semantic success/warning/error colors, and base-icon inheritance.

## Mouse pointers

Light uses `breeze_cursors`; Dark uses `Breeze_Light`, both at 18 px. A pointer
change must agree across `config/settings.json`, global-theme `contents/defaults`,
installer dependency checks, GTK settings, the live cursor command, and
`scripts/login.py`. Keep the two login helpers identical and update their tests.

## Panels

Each variant keeps installation logic in `scripts/layout.js` and a native copy at
`assets/plasma/look-and-feel/<ID>/contents/layouts/org.kde.plasma.desktop-layout.js`.
The installer substitutes `__WALLPAPER_URI__` with the target directory. The native
copy uses `"file://" + userDataPath("data") + "/wallpapers/Moe"` or `MoeDark`;
never add a personal absolute path. Tests compare the two forms.

Panel height is `panel.height = 32`; the initial pinned-task list is
`tasks.writeConfig("launchers", "")`. Launcher icons are set both in the layout
and in `scripts/launcher.js`, which updates existing panels without recreating them.
Both paths also set the Peek at Desktop icon to `view-grid-symbolic`.
The tray clipboard icon resolves `klipper-symbolic` to the existing Papirus
clipboard artwork at 16, 22, and 24 px.
Edits do not affect existing panels until applied. Use `--layout` only when panel
replacement is intended; normal `--apply` already updates both panel icons.

### Optional CPU, RAM, and weather widgets

For a compact panel, place System Monitor and Open-Meteo Weather Card between
the tray and the clock. The default layout has no dependency on these optional
widgets. Use the [Text with Icon sensor face](https://github.com/PatrickSzela/libksysguard-texticon)
with sensors `cpu/all/usage` and `memory/physical/used`. Set spacing to 3 px,
choose 16 px icons `cpu-symbolic` and `drive-ram-symbolic`, and arrange the
formatter as icon, CPU value, icon, RAM value. Use precision 0 for CPU and 1
for RAM. The formatter needs no spacer entry.

For [Open-Meteo Weather Card](https://github.com/tiamed/plasma-openmeteo-weather),
the tested customization sets the compact row spacing to 3 px. In
`contents/ui/CompactRepresentation.qml`, use `content.implicitWidth` for the
horizontal minimum and preferred widths when temperature text is visible.
Remove the temperature label's fill-width and width-dependent maximum to let
the row size to its contents. Reload Plasma Shell after editing QML.

## Optional window blur

[KWin Effects Glass](https://github.com/4v3ngR/kwin-effects-glass#usage) is a
separate effect. Install a build for the exact running KWin version. Use Glass
in place of the built-in Blur effect. In Glass, use a class allowlist with
`org.kde.dolphin`, `org.kde.konsole`, and `plasmashell` so the panel and launcher
can also receive blur. Use a decoration allowlist containing only
`org.kde.dolphin` and `org.kde.konsole`, keep **Ignore content blur region** off,
and use the declared corner radius. Set active and inactive opacity to 90%
with application-specific KWin rules for Dolphin and Konsole. This makes their
whole windows translucent, including text and icons.

The third-party Rounded Corners shader can create artifacts on Aurorae
decorations. If using it, exclude Dolphin, Konsole, and any other decorated
applications that show doubled corners. The theme installer leaves KWin
effects and opacity rules to the user.

## Wallpaper and lock screen

Sources are `light/assets/wallpapers/Moe/` and `dark/assets/wallpapers/MoeDark/`.
Keep light images in `contents/images/` and dark images in `contents/images_dark/`.
Update metadata, previews, credits, and adaptation records when replacing images.
Reference the package directory to retain adaptive desktop/lock-screen behavior.
The login helper selects a specific image in `scripts/login.py`; update its
filename references if image names or dimensions change.

## Konsole and Fish

Each variant ships both `.profile` and `.colorscheme` files under `assets/konsole/`.
Keep corresponding copies synchronized.

In profiles, `[Appearance]` selects font/palette and `[General]` selects shell and
initial dimensions. `[Cursor Options]` uses RGB `CustomCursorColor` when
`UseCustomCursorColor=true`; `[Terminal Features]` controls
`BlinkingCursorEnabled` and `AnimatingCursorEnabled`.

`LightThemeProfile` and `DarkThemeProfile` in `config/settings.json` use profile
display names; `DefaultProfile` uses a filename. Update all references when
renaming a profile. Greeting, ANSI colors, and Pure settings live in
`assets/fish/papirus-breeze.fish`. Do not replace the user's whole Fish or
distribution configuration to change presentation.

## Validate and reinstall

After reviewing intentional edits:

```bash
python3 tools/project.py manifest
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
python3 install.py install --apply light
```

The final command changes the live session; run it only when you intend to apply
the theme. For one variant's maintenance, use `--variant light` or `--variant dark`.
Manifest refresh accepts local contents as the integrity baseline; it does not
repair a damaged download. Reopen Konsole for changed profiles; cached icons may
need application or session restart. Read [recovery instructions](RESTORE_AND_TROUBLESHOOTING.md)
before restoring complete snapshots.
