// SPDX-License-Identifier: GPL-3.0-only
// __WALLPAPER_URI__ is replaced by the installer with the destination XDG path.
var image = __WALLPAPER_URI__;
desktops().forEach(function (desktop) {
    desktop.wallpaperPlugin = "org.kde.image";
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktop.writeConfig("Image", image);
    desktop.writeConfig("PreviewImage", image);
    desktop.reloadConfig();
});
