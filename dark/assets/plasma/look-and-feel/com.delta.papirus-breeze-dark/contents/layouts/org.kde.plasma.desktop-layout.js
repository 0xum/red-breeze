// SPDX-License-Identifier: GPL-3.0-only
// Rebuilds one floating, 32 px bottom panel per connected screen.
// Shared by the installer and the native global-theme layout reset.
panels().forEach(function (panel) { panel.remove(); });
for (var screen = 0; screen < screenCount; screen++) {
    var panel = new Panel;
    panel.screen = screen;
    panel.location = "bottom";
    panel.height = 32;
    panel.alignment = "center";
    panel.lengthMode = "fill";
    panel.floating = true;
    panel.hiding = "none";
    panel.opacity = "adaptive";

    var launcher = panel.addWidget("org.kde.plasma.kickoff");
    launcher.currentConfigGroup = ["General"];
    // The editable SVG is bundled in both icon themes.
    launcher.writeConfig("icon", "papirus-breeze-launcher");
    if (screen === 0) {
        launcher.currentConfigGroup = ["Shortcuts"];
        launcher.writeConfig("global", "Alt+F1");
    }
    panel.addWidget("org.kde.plasma.pager");
    var tasks = panel.addWidget("org.kde.plasma.icontasks");
    tasks.currentConfigGroup = ["General"];
    tasks.writeConfig("launchers", "");
    panel.addWidget("org.kde.plasma.marginsseparator");
    panel.addWidget("org.kde.plasma.systemtray");
    panel.addWidget("org.kde.plasma.digitalclock");
    panel.addWidget("org.kde.plasma.showdesktop");
}

// userDataPath("data") respects the destination user's XDG data directory.
var wallpaper = "file://" + userDataPath("data") + "/wallpapers/MoeDark";
desktops().forEach(function (desktop) {
    desktop.wallpaperPlugin = "org.kde.image";
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktop.writeConfig("Image", wallpaper);
    desktop.writeConfig("PreviewImage", wallpaper);
    desktop.reloadConfig();
});
