# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('DBus', '1.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Dbus, GLib, Gio, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from Bar import Bar
from Launcher import Launcher

def on_activate(app):
	Bar(app)
	Launcher(app)

app = Gtk.Application(application_id='ushell.SwayShell')
app.connect('activate', on_activate)
app.run()

# register dbus connection at ushell.SwayShell with object /ushell/SwayShell implementing interface ushell.SwayShell
#
# when a "Launcher" message is received from dbus, show the launcher
#
# when a "Dim" message is received from dbus, create an empty window, with app_id swaydim
# when it's focused, first executes "swaymsg [workspace=__focused__ floating] kill", the closes itself
#
# when a "Lock" message is received from dbus, lock
# when a "LockBattery" message is received from dbus, lock if on battery

# when screens are added/removed:
# , move bar to first output: LayerShell.set_monitor(bar_gtkwindow, gdkmonitor)
# , take the list of workspaces (using swaymsg)
# , move the first non'numeric workspace to the first output (and turn it on)
# , move workspace 2 ... to output 2 ...
# this way, the first monitor will always remains the main monitor, even after reconnecting
# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
# https://docs.gtk.org/gdk4/class.Monitor.html
# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
# https://github.com/tamirzb/qkdisplays

# turn off empty outputs (except the primary one)

# https://www.freedesktop.org/wiki/Software/systemd/inhibit/

# on screen keyboard for touch screen
# https://github.com/fortime/fcitx5-osk
# https://wiki.archlinux.org/title/Fcitx5

# voice control: keybindings and typing
# https://www.speedofsound.io/
# https://github.com/kavehtehrani/speech2text-extension/
# https://github.com/k2-fsa/sherpa-onnx
# https://github.com/Saim20/willow
# https://github.com/Manish7093/IBus-Speech-To-Text
# https://github.com/canonical/myna
# https://github.com/mkiol/dsnote
# https://easyspeak.dev/latest/
# https://github.com/g0dd4rd/anthony/

# vocal feedback for commands
# https://project-spiel.org/

# run uni.desktop

# [ -e "$HOME"/.config/ushell/autostart ] && sh "$HOME"/.config/ushell/autostart
