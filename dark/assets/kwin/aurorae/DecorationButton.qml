/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration

Item {
    id: button
    property int buttonType : DecorationOptions.DecorationButtonNone
    property bool hovered: false
    property bool pressed: false
    property bool toggled: false
    readonly property bool customMotion: (auroraeTheme.themeName === "Moe" || auroraeTheme.themeName === "MoeDark")
    property bool actionPending: false
    NumberAnimation {
        id: fadeOut
        target: button
        property: "opacity"
        from: 1
        to: 0
        duration: 140
        easing.type: Easing.InQuad
        onFinished: {
            if (button.buttonType === DecorationOptions.DecorationButtonMinimize)
                decoration.requestMinimize();
            else if (button.buttonType === DecorationOptions.DecorationButtonClose)
                decoration.requestClose();
            button.opacity = 1;
            button.actionPending = false;
        }
    }
    enabled: {
        switch (button.buttonType) {
        case DecorationOptions.DecorationButtonClose:
            return decoration.client.closeable;
        case DecorationOptions.DecorationButtonMaximizeRestore:
            return decoration.client.maximizeable;
        case DecorationOptions.DecorationButtonMinimize:
            return decoration.client.minimizeable;
        case DecorationOptions.DecorationButtonExplicitSpacer:
            return false;
        default:
            return true;
        }
    }
    MouseArea {
        anchors.fill: parent
        acceptedButtons: {
            switch (button.buttonType) {
            case DecorationOptions.DecorationButtonMenu:
                return Qt.LeftButton | Qt.RightButton;
            case DecorationOptions.DecorationButtonMaximizeRestore:
                return Qt.LeftButton | Qt.RightButton | Qt.MiddleButton;
            default:
                return Qt.LeftButton;
            }
        }
        enabled: !button.actionPending
        hoverEnabled: true
        onEntered: button.hovered = true
        onExited: button.hovered = false
        onPressed: button.pressed = true
        onReleased: button.pressed = false
        onClicked: {
            switch (button.buttonType) {
            case DecorationOptions.DecorationButtonMenu:
                // menu
                decoration.requestShowWindowMenu();
                break;
            case DecorationOptions.DecorationButtonApplicationMenu:
                // app menu
                var pos = button.mapToItem(null, 0, 0); // null = "map to scene"
                decoration.requestShowApplicationMenu(Qt.rect(pos.x, pos.y, button.width, button.height), 0)
                break;
            case DecorationOptions.DecorationButtonOnAllDesktops:
                // all desktops
                decoration.requestToggleOnAllDesktops();
                break;
            case DecorationOptions.DecorationButtonQuickHelp:
                // help
                decoration.requestContextHelp();
                break;
            case DecorationOptions.DecorationButtonMinimize:
                // minimize
                if (button.customMotion) {
                    button.actionPending = true;
                    fadeOut.restart();
                } else {
                    decoration.requestMinimize();
                }
                break;
            case DecorationOptions.DecorationButtonMaximizeRestore:
                // maximize
                decoration.requestToggleMaximization(mouse.button);
                break;
            case DecorationOptions.DecorationButtonClose:
                // close
                if (button.customMotion) {
                    button.actionPending = true;
                    fadeOut.restart();
                } else {
                    decoration.requestClose();
                }
                break;
            case DecorationOptions.DecorationButtonKeepAbove:
                // keep above
                decoration.requestToggleKeepAbove();
                break;
            case DecorationOptions.DecorationButtonKeepBelow:
                // keep below
                decoration.requestToggleKeepBelow();
                break;
            case DecorationOptions.DecorationButtonShade:
                // shade
                decoration.requestToggleShade();
                break;
            }
        }
        onDoubleClicked: {
            if (button.buttonType == DecorationOptions.DecorationButtonMenu) {
                decoration.requestClose();
            }
        }
        Component.onCompleted: {
            switch (button.buttonType) {
            case DecorationOptions.DecorationButtonOnAllDesktops:
                // all desktops
                button.toggled = Qt.binding(function() { return decoration.client.onAllDesktops; });
                break;
            case DecorationOptions.DecorationButtonKeepAbove:
                button.toggled = Qt.binding(function() { return decoration.client.keepAbove; });
                break;
            case DecorationOptions.DecorationButtonKeepBelow:
                button.toggled = Qt.binding(function() { return decoration.client.keepBelow; });
                break;
            case DecorationOptions.DecorationButtonShade:
                button.toggled = Qt.binding(function() { return decoration.client.shaded; });
                break;
            }
        }
    }
}
