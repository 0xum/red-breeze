# Credits, adaptations, and licenses

Each component retains its own license. License texts and the Papirus author list
are included in `LICENSES/`. Original authorship remains in asset metadata.

| Component | Source / author | License | Adaptation in this package |
| --- | --- | --- | --- |
| Moe Light | jomada, version 1.1; original metadata included | CC-BY-SA-4.0 | Original light image and metadata retained; image also used as a preview |
| Amy-Light-Aurorae-6 | l4k1, version 1.2; original metadata included | GPL-3.0 (metadata: GPLv3) | Original decoration files retained |
| Papirus Breeze Light palette | Based on KDE Breeze Light; authors in the `.colors` header | LGPL-2.0-or-later | Exported/adapted palette, red `#E93D58` accent, distinct scheme name |
| Papirus / Catppuccin folders | [Papirus Development Team](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), [Catppuccin papirus-folders](https://github.com/catppuccin/papirus-folders) | GPL-3.0 and retained Catppuccin MIT notice | 835 red folder aliases; remaining icons inherit the installed base theme |
| Scripts, terminal profiles, launcher, and composition | Delta, 2026 | GPL-3.0-only | Original integration and theme-specific adaptations |

The adaptive wallpaper includes original Moe Light by jomada and Moe Dark adapted
by Delta using ImageGen. Both images are distributed under CC-BY-SA-4.0. The dark
image is in `contents/images_dark/`; see the wallpaper's `ADAPTATION.md` and
`GENERATION.md` for provenance. Original light metadata remains included.

Of the folder aliases, 539 use unchanged Papirus Red SVGs and 7 Copy Cloud icons
retain Catppuccin/Papirus geometry recolored to Papirus Red (`#e25252`, `#bf4b4b`).
A further 289 aliases resolve to red SVGs, including `inode-directory`,
`gtk-directory`, `stock_folder`, and cross-category shortcuts.

System icons derive from Papirus SVGs (GPL-3.0), with neutral glyphs converted to
`#E93D58`. `PapirusBreezeRed` adapts KDE Visual Design Group Breeze sprites whose
original license metadata is LGPL. Original metadata is retained in
`LICENSES/Breeze-original-metadata.json`; surfaces and other resources inherit the
installed Breeze style.

Dolphin icons retain original Papirus geometry/cutouts, recolored from blue to
`#E93D58` with `#a62a3e` shading (GPL-3.0). Empty/full trash icons and symbolic
aliases retain Papirus geometry/shading with gray changed to red (GPL-3.0).
Explicit `user-trash` aliases prevent fallback to a user avatar.

The Konsole profiles/palettes and compact Fish configuration under `assets/konsole/`
and `assets/fish/` are original package adaptations under GPL-3.0-only. Pure,
Fish/Konsole applications, fonts, Ocean sounds, Breeze, and the full Papirus
library are external dependencies and are not redistributed in full.

English documentation does not replace original legal notices or upstream
localized metadata. Preserve attribution and license files in distributions.
