// SPDX-License-Identifier: GPL-3.0-only
// Update existing launchers without rebuilding panels or changing pinned apps.
panels().forEach(function (panel) {
    panel.widgets().forEach(function (widget) {
        if (["org.kde.plasma.kickoff", "org.kde.plasma.kicker", "org.kde.plasma.kickerdash"].indexOf(widget.type) !== -1) {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("icon", "papirus-breeze-launcher");
            widget.reloadConfig();
        }
    });
});
