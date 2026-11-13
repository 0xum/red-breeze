// SPDX-License-Identifier: GPL-3.0-only
// Update existing launcher and Peek at Desktop icons without rebuilding panels.
panels().forEach(function (panel) {
    panel.widgets().forEach(function (widget) {
        var icon;
        if (["org.kde.plasma.kickoff", "org.kde.plasma.kicker", "org.kde.plasma.kickerdash"].indexOf(widget.type) !== -1) {
            icon = "papirus-breeze-launcher";
        } else if (widget.type === "org.kde.plasma.showdesktop") {
            icon = "view-grid-symbolic";
        } else {
            return;
        }
        widget.currentConfigGroup = ["General"];
        widget.writeConfig("icon", icon);
        widget.reloadConfig();
    });
});
