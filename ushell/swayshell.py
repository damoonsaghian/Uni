# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('DBus', '1.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Gio, Gdk, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from bar import setup_bar
from launcher import setup_launcher
from locker import setup_locker
from osk import setup_osk

def setup_screens():
	pass
	# when screens are added/removed:
	# , move bar to first output: LayerShell.set_monitor(bar_gtkwindow, gdkmonitor)
	# , take the list of workspaces (using swaymsg)
	# , move the first non'numeric workspace to the first output (and turn it on)
	# , move workspace 2 ... to output 2 ...
	# this way, the first monitor will always remains the main monitor, even after reconnecting
	# display = Gdk.Display.get_default()
	# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
	# https://docs.gtk.org/gdk4/class.Monitor.html
	# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
	# https://github.com/tamirzb/qkdisplays
	
	# ~/.config/ushell/screens
	# turn off empty outputs (except the primary one)

def setup_voice_control():
	pass
	# voice control: keybindings (speaking while holding "mod" or "ctrl") and typing
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

def on_startup(app):
	setup_bar(app)
	setup_launcher(app)
	setup_locker(app)
	setup_osk(app)
	
	def dim():
		# create an empty window with title "dim"
		# when it's focused, first executes "swaymsg [workspace=__focused__ floating] kill", then closes itself
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.SwayShell", "Dim", "/ushell/SwayShell", None, Gio.DBusSignalFlags.NONE, dim)
	
	setup_screens()
	setup_voice_control()
	
	# run uni.desktop
	
	# [ -e "$HOME"/.config/ushell/autostart ] && sh "$HOME"/.config/ushell/autostart

Gtk.Settings.get_default().props.gtk_overlay_scrolling = False

app = Gtk.Application(application_id='ushell.SwayShell')
app.connect('activate', on_activate)
app.run()
