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
Edits do not affect existing panels until applied. Use `--layout` only when panel
replacement is intended. Normal `--apply` updates the launcher and Peek at Desktop.

### Clipboard tray icon

The Plasma 6.8 clipboard widget requests `klipper-symbolic`. Both icon themes
supply that name with the compact Papirus `clipboard.svg` artwork. This changes
the glyph inside the existing tray slot. In each variant, look under
`assets/icons/PapirusBreezeLight/` or `assets/icons/PapirusBreezeDark/` for
`16x16/panel/klipper-symbolic.svg`, `22x22/panel/klipper-symbolic.svg`, and
`24x24/panel/klipper-symbolic.svg`. Keep each file in sync with the
`clipboard.svg` in the same directory. If the old glyph is cached after
reinstalling, reload Plasma Shell.

### Optional CPU, RAM, and weather widgets

In the reference layout, the order after the system tray is **CPU and RAM,
weather, clock, Peek at Desktop**. Add the optional widgets to each panel you
want to customize. The bundled layout runs without them.

#### CPU and RAM

Add **System Monitor**, then select the
[Text with Icon sensor face](https://github.com/PatrickSzela/libksysguard-texticon).
Choose `cpu/all/usage` and `memory/physical/used` as the high-priority sensors,
in that order. Disable the title in the compact panel. In the face settings,
set spacing to **3 px** (previously 4 px) and use this formatter:

| Entry | Value |
| --- | --- |
| CPU icon | `cpu-symbolic`, 16 px |
| CPU value | Sensor 0, precision 0 |
| RAM icon | `drive-ram-symbolic`, 16 px |
| RAM value | Sensor 1, precision 1 |

Remove the blank text entry between the CPU value and RAM icon. The same
3 px spacing then applies between all four entries.

#### Weather

Add [Open-Meteo Weather Card](https://github.com/tiamed/plasma-openmeteo-weather),
select system icons and Celsius, and enable temperature text in the panel.
In the installed widget's `contents/ui/CompactRepresentation.qml`, apply the
following changes to the compact representation:

- Set `spacing: 3` on the `RowLayout` with `id: content`.
- When temperature text is visible, use `content.implicitWidth` for the
  compact item's horizontal minimum and preferred widths. Keep the existing
  icon-only width values for the other states.
- Remove `Layout.fillWidth: true` and the width-dependent
  `Layout.maximumWidth` from the temperature label so the row can use its
  natural width.

This removes the extra space around the weather reading and brings it closer
to the clock. Reload Plasma Shell after editing QML. A widget update may
overwrite the local change.

## Optional window effects

Both official themes include the Rounded Corners settings described below in
their global-theme defaults and installer profiles. The effect plugin and its
Aurorae compatibility patch are still external prerequisites. Theme selection
requests the effect; it does not install the plugin.

The complete package also includes a reversible Glass blur and window-opacity
profile for Plasma Wayland that reapplies the same rounding settings. Restore
returns to the settings captured when the helper was applied, which may already
include the official theme's rounding profile.

```sh
python3 tools/window-effects.py apply
python3 tools/window-effects.py restore
```

Before a system upgrade blocked by these local plugins' exact KWin dependencies:

```sh
python3 tools/window-effects.py prepare-upgrade
sudo pacman -Syu
```

Run the helper as your normal user in Plasma Wayland. It requests sudo through
its terminal, backs up KWin configuration and package versions under
`$XDG_STATE_HOME/papirus-breeze/kwin-upgrade-*`, disables the custom effects,
enables built-in blur, and removes only the two local effect packages using
pacman's normal dependency checks and confirmation. If removal fails or is
cancelled, the effects stay disabled and the backup remains; rerun to retry.
The helper does not perform the system upgrade. Log out and back in after the
upgrade. Existing patch files and cached package archives are preserved, but
old binaries must not be reinstalled against a different KWin version.
Rebuild compatible plugins with the desired patches before enabling them.
If a managed profile still exists, restore it after rebuilding, then apply again.
Do not loosen the dependency pin or use `--nodeps` to bypass compatibility.

Install both plugins before applying the profile. KWin requires plugins built
against the exact running version. The reference setup used KWin 6.8.2 with
[KWin Effects Glass](https://github.com/4v3ngR/kwin-effects-glass) at
`5e2845fffbe893177c091fe18d603b9095cc2729` and
[KDE Rounded Corners 0.11.0](https://github.com/matinlotfali/KDE-Rounded-Corners/tree/v0.11.0).
Follow each upstream project's build and installation instructions for Wayland.
From the Rounded Corners source checkout, apply the bundled
[compatibility patch](../tools/rounded-corners-aurorae.patch) before building.

```sh
git apply --unidiff-zero /path/to/red-breeze/tools/rounded-corners-aurorae.patch
```

The profile uses Glass in place of the built-in Blur effect. It enables blur
for Dolphin, Konsole, and Plasma Shell, including the panel and launcher.
Dolphin and Konsole receive 90% active and inactive window opacity, which
also affects their text and icons.

Rounded Corners uses an 11 px radius and native shadows, with extra outlines
disabled. The compatibility patch bypasses the shader on windows with
KWin-drawn decorations to avoid doubled corners on Moe and MoeDark. Dolphin
and Konsole are also excluded explicitly. Maximized and fullscreen windows
are excluded from rounding.

The helper snapshots the affected keys and loaded effects under
`$XDG_STATE_HOME/papirus-breeze/window-effects.json` (default
`~/.local/state/papirus-breeze/window-effects.json`). Restore the profile before
uninstalling either effect. The helper's snapshot is separate from theme
installation and removal; theme selection can update the rounding settings while the helper is active.

## Wallpaper and lock screen

Sources are `light/assets/wallpapers/Moe/` and `dark/assets/wallpapers/MoeDark/`.
Keep light images in `contents/images/` and dark images in `contents/images_dark/`.
Update metadata, previews, credits, and adaptation records when replacing images.
Reference the package directory to retain adaptive desktop/lock-screen behavior.
The login helper selects a specific image in `scripts/login.py`; update its
filename references if image names or dimensions change.

To disable the clock and date shadow on the Plasma 6.8.2 lock screen:

```sh
sudo python3 tools/lockscreen-clock.py apply
sudo python3 tools/lockscreen-clock.py restore
```

The helper changes only the clock shadow visibility in the installed
`LockScreenUi.qml`. The next lock uses the new appearance. Plasma updates may
replace this file. The helper checks for the known QML before changing it.

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
