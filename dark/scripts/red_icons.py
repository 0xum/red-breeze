#!/usr/bin/env python3
"""Build red native SVG variants without changing the application text palette."""
# SPDX-License-Identifier: GPL-3.0-only
import colorsys
import re
import xml.etree.ElementTree as ET

RED = "#E93D58"
TEXT_ROLES = {"ColorScheme-Text", "ColorScheme-ViewText", "ColorScheme-ButtonText", "ColorScheme-WindowText", "ColorScheme-ComplementaryText"}
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")


def red_svg(source, system_application=False):
    """Return a variant or None when the icon has no neutral foreground to recolor.

    Detach neutral glyphs from ColorScheme-Text so KDE cannot turn them back into
    black/white. Keep positive, warning and error roles and background cutouts.
    """
    root = ET.fromstring(source)
    changed = False
    for element in root.iter():
        roles = set(element.get("class", "").split())
        if roles & TEXT_ROLES:
            roles -= TEXT_ROLES
            if roles:
                element.set("class", " ".join(sorted(roles)))
            else:
                element.attrib.pop("class", None)
            for key in ("fill", "stroke", "color", "stop-color", "style"):
                if key in element.attrib:
                    element.set(key, re.sub("currentColor", RED, element.get(key), flags=re.I))
            style = element.get("style", "").rstrip(";")
            element.set("style", style + ";color:" + RED)
            changed = True

    # Some symbolic icons use literal paint rather than a KDE color role.
    paints = []
    for element in root.iter():
        if element.tag.endswith("style"):
            continue
        for key in ("fill", "stroke"):
            value = element.get(key, "")
            if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                paints.append(value.lower())
        paints.extend(v.lower() for v in re.findall(r"(?:fill|stroke)\s*:\s*(#[0-9a-fA-F]{6})\b", element.get("style", "")))
    unique = set(paints)
    plain_monochrome = not changed and len(unique) == 1 and all(
        max(int(c[i:i+2], 16) for i in (1, 3, 5)) - min(int(c[i:i+2], 16) for i in (1, 3, 5)) <= 20 for c in unique
    )

    def paint(value):
        nonlocal changed
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            return value
        rgb = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
        if plain_monochrome:
            changed = True
            return RED
        # Colored system-preference pictograms keep their shading and cutouts.
        if system_application and max(rgb) - min(rgb) > 0.12:
            hue, saturation, brightness = colorsys.rgb_to_hsv(*rgb)
            hue = colorsys.rgb_to_hsv(233/255, 61/255, 88/255)[0]
            recolored = colorsys.hsv_to_rgb(hue, saturation, brightness)
            changed = True
            return "#" + "".join(f"{round(v*255):02x}" for v in recolored)
        return value

    for element in root.iter():
        if element.tag.endswith("style"):
            continue
        for key in ("fill", "stroke"):
            if key in element.attrib:
                element.set(key, paint(element.get(key)))
        if "style" in element.attrib:
            element.set("style", re.sub(r"((?:fill|stroke)\s*:\s*)(#[0-9a-fA-F]{6})\b", lambda m: m[1] + paint(m[2]), element.get("style")))
    if not changed:
        return None
    root.set("style", root.get("style", "").rstrip(";") + ";color:" + RED)
    return ET.tostring(root, encoding="unicode") + "\n"
