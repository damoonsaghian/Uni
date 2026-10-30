from gi.repository import Gtk as gtk

def prompt_view():
	pass

# results are placed in a vertical stack
# older result viewa will be shrinked to a single line, when not focused
# to navigate between results, use "ctrl+pageup" and "ctrl+pagedown" keys

# terminal commands
# https://gist.github.com/carlos-jenkins/268c562846eec2303e0ffb881c580f4e
# two modes: normal, sudo
# for sudo mode: vte.Terminal.spawn_async(argv=['bash', '-c', command])
# for normal mode:
# vte.Terminal.spawn_async(argv=[
# 'bwrap', '--bind', '/', '/', '--bind', '/dev/null', '"$SWAYSOCK"',
# --bind "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"-sandbox "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
# --bind /dev/null /usr/bin/lisgd \
# '--', 'bash', '-c', command
# ])
#
# scroll up: Page_Up
# scroll down: Page_Down
# copy: Control+c
# paste: Control+v
# make "ctrl q" to act like "ctrl c" (ie "\x03" character)

# screenshot and screencast
# when finished, move the file to clipboard
# grim -o "$$HOME/.cache/screen.png" | wl-copy --type text/uri-list "file://$$HOME/.cache/screen.png"

# https://github.com/heidefinnischen/cuneo
# https://qalculate.github.io/
# libqalculate-progs

# exchange rates and currency data
# https://frankfurter.dev/

# https://python-weather.readthedocs.io/en/latest/
# https://gnome.pages.gitlab.gnome.org/libgweather/
