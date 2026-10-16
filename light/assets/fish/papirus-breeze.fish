# SPDX-License-Identifier: GPL-3.0-only
# Loaded after the user's config, so a distribution greeting cannot replace it.
function fish_greeting --description 'Compact Papirus Breeze system summary'
    set -l os_name (uname -s)
    if test -r /etc/os-release
        set -l pretty (command awk -F= '$1 == "PRETTY_NAME" {gsub(/^"|"$/, "", $2); print $2; exit}' /etc/os-release)
        if test -n "$pretty"
            set os_name $pretty
        end
    end
    set -l desktop "$XDG_CURRENT_DESKTOP"
    if set -q KDE_SESSION_VERSION
        set desktop "Plasma $KDE_SESSION_VERSION"
    else if test -z "$desktop"
        set desktop Linux
    end
    printf '\n'
    set_color --bold red
    printf '  %s' "$os_name"
    set_color normal
    printf ' · %s\n' (uname -m)
    set_color brblack
    printf '  Linux %s\n' (uname -r)
    printf '  %s · fish %s\n' "$desktop" "$version"
    set_color normal
    printf '\n'
end

# Keep the existing prompt implementation; compact Pure when it is installed.
set -g pure_enable_single_line_prompt true
set -g pure_color_primary red
set -g pure_color_prompt_on_success red
set -g pure_color_current_directory normal
set -g pure_color_git_branch brblack
set -g pure_show_system_time false
set -g pure_separate_prompt_on_error false

# ANSI colors follow the active Konsole Light/Dark profile automatically.
set -g fish_color_normal normal
set -g fish_color_command normal
set -g fish_color_param normal
set -g fish_color_error red
set -g fish_color_quote green
set -g fish_color_redirection red
set -g fish_color_operator red
set -g fish_color_comment brblack
set -g fish_color_autosuggestion brblack
