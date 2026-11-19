# Papirus Breeze internal corners

Native KWin 6.8.3 effect for decorated normal windows and dialogs using Moe or
MoeDark. All four content corners use an 8 logical-pixel radius and are filled
with the adjacent decoration border color. A 1 logical-pixel inset outline follows
the same rounded rectangle, with Breeze separator color (Window/WindowText mixed
at the KDE frameContrast setting). Maximized, fullscreen, undecorated,
and other-theme windows are excluded. The effect runs after Glass/Breeze blur
(chain position 99), so offscreen rendering does not swallow backdrop blur.

Source license: GPL-3.0-only. Build against the exact installed KWin and Qt private
headers. The shader is embedded in the native plugin. Binary installation uses
Polkit; theme configuration and user assets remain per-user. See the standalone
package README and `scripts/inner_corners.py --help` for installation and removal.
