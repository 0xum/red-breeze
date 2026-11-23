# Changelog

This file records known changes. An entry does not imply a published release or tag.

## Unreleased

- Add an opt-in ChatGPT desktop profile with Glass blur, 90% window opacity, and 11 px rounded corners. Both themes exclude ChatGPT by default.

- Refresh the internal-outline color automatically on palette, decoration, and KWin configuration changes so switching to Light cannot leave a cached Dark outline.

- Add a 1 px inset outline to the full internal rounded perimeter for every Moe/MoeDark decorated application. Match Breeze/Dolphin separator colors using the active palette and frame contrast; retain 8 px corners and backdrop blur.

- Default both themes to four 8 px internal content corners filled with the decoration border; support every Moe/MoeDark decorated application and preserve backdrop blur by drawing after Glass. Bundle native source and a version-specific build/install/recovery helper.

- Make symbol-free Moe/MoeDark circles, hover growth, maximize/restore bounce, and minimize/close fade-out the default; bundle the shared per-user Aurorae QML runtime with installer backup/recovery.

- Include the 11 px Rounded Corners profile in both official global themes and installer settings; retain Glass blur and opacity as opt-in.

- Use the Papirus accent for normal greeter text and disable the clock shadow in the installed SDDM theme copy.

- Use jomada’s Moe and MoeDark 1.9 Aurorae decorations by default and retain Amy as an alternative.
- Use a compact clipboard icon and the grid icon for Peek at Desktop in both variants.
- Add a reversible Wayland profile for Glass blur and Rounded Corners, including the Aurorae compatibility patch.
- Document the optional compact panel widgets.

- Configure administrative Light/Dark login following from the unified installer by default; add `--no-login`.
- Set an adaptive wallpaper on the native lock screen while preserving lock/security preferences.
- Read nested KConfig groups correctly so wallpaper references are cleaned up during removal.
- Support explicit XDG configuration sources for login watching and restart the watcher after updates.
- Add a unified installer with a menu, prerequisite checks, installation, updates, and removal.
- Register the Light/Dark Quick Settings pair and restore previous choices on removal.
- Preserve customized resources, third-party profiles, dependencies, and backups during removal.
- Build a complete distribution archive in `dist/` alongside the standalone packages.
- Use a dark mouse pointer in Light and a white pointer in Dark, including GTK and login; keep 18 px sizing.
- Make English the default for documentation and command-line messages; provide an optional pt-BR guide.
- Add repository-level agent instructions and a `.agents/` guide to maintenance workflows.

## Unified repository — October 16, 2026

- Combine Light and Dark under `light/` and `dark/`, with one Git repository at the root.
- Record the original repositories' history in external bundles and metadata on the source workstation.
- Centralize installation, appearance, customization, development, and recovery documentation.
- Add one tool for integrity checks, tests, manifest updates, and packaging.
- Preserve the visual version imported at the time: 1.0.11. The directory reorganization did not change the installed desktop.

## 1.0.13

- Include palette, red accent, icons, cursor, and wallpaper in login appearance.
- Make greeter assets accessible outside the user's private home directory.
- Adapt greeter complementary colors to the selected Light/Dark window colors.
- Add optional per-user theme following through systemd path/service units and fixed administrative profiles.
- Support Plasma Login Manager and SDDM while preserving authentication and autologin.

## 1.0.12

- Add explicit `user-trash` and `user-trash-full` icons so Dolphin does not fall back to a user avatar.
- Include empty/full red trash icons and symbolic aliases with the original geometry.
- Check that these aliases exist and do not use the user icon's geometry.

## 1.0.11

- Replace the launcher's center with a real transparent cutout using `fill-rule="evenodd"`.

## 1.0.10

- Add an editable red rounded hexagonal launcher SVG with a transparent circular center.
- Include it in both icon themes, native layouts, and existing-panel updates.

## 1.0.9

- Use a red block cursor with blinking and animation in both Konsole profiles.

## 1.0.8

- Add Light/Dark Konsole profiles with native system-theme synchronization.
- Use JetBrainsMono Nerd Font 11 pt and an initial 96 × 24 terminal size.
- Add a three-line Fish greeting and compact single-line Pure settings while retaining distribution configuration.

## Original theme set

- Export Light/Dark themes, adaptive wallpapers, lock-screen settings, and login installers.
- Include an optional native 32 px panel per connected monitor with no pinned applications.
- Provide red folders, system icons, Dolphin icons, and Plasma sprites.
- Include installation backups, restoration, tests, SHA-256 manifests, and independent packaging.
