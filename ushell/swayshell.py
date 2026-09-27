import subprocess

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
	# , move bar and launcher to first output: LayerShell.set_monitor(bar_gtkwindow, gdkmonitor)
	# , take the list of workspaces (using swaymsg)
	# , move the first non'numeric workspace to the first output (and turn it on)
	# , move workspace 2 ... to output 2 ...
	# this way, the first monitor will always remains the main monitor, even after reconnecting
	# display = Gdk.Display.get_default()
	# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
	# https://docs.gtk.org/gdk4/class.Monitor.html
	# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
	# https://github.com/tamirzb/qkdisplays
	
	# run comands in ~/.config/ushell/screens using swaymsg
	# focus the first monitor
	# turn off empty outputs (except the primary one)
	
	# if screen is landscape: width=80 height=80 pos="center"
	# if screen is portraut: width=100 height=80 pos="0 ppt 20 ppt"
	# ["swaymsg", f"for_window [floating workspace={num}] resize set {width} ppt {haight} ppt; move position {pos}"]
	
	subprocess.run(["swaymsg", "bindswitch lid:on output - disable"])
	subprocess.run(["swaymsg", "bindswitch lid:off output * enable"])

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
	# swaymsg:
	# output * bg #222222 solid_color
	# for_window [all] border csd
	#
	# input type:touchpad {
	# 	tap enabled
	# 	scroll_method two_finger
	# 	natural_scroll enabled
	# }
	# seat * hide_cursor 8000
	#
	# bindsym Mod4+BackSpace kill
	# bindsym Mod1+Escape kill
	# bindsym button3 kill
	
	# when the state of a window changes:
	# if the focused window is tiling, kill all floating windows of current workspace,
	# 	then if it's not the first window of workspace, make it floating
	# if the focused window is floating, and there is no dimmer, open one
	# { swaymsg -m -t subscribe "[\"window\"]" || swaynag -m "floater failed"; } | while read _; do \
	# 	if swaymsg "[con_id=__focused__ tiling] focus"; then \
	# 		swaymsg "[workspace=__focused__ floating] kill"; \
	# 		swaymsg focus prev && swaymsg "focus next; floating enable"; \
	# 	elif swaymsg "[con_id=__focused__ floating] focus" && \
	# 		! swaymsg "[workspace=__focused__ app_id="ushell.SwayShell" title=dimmer] floating enable"; \
	# 	then \
	# 		dbus-send --dest=ushell.SwayShell /ushell/SwayShell ushell.SwayShell.Dim; \
	# 	fi; \
	# done'
	#
	# no_focus [app_id="ushell.SwayShell" title=dimmer]
	# for_window [app_id="ushell.SwayShell" title=dimmer] opacity 0.5, floating enable, \
	# 	resize set 100 ppt 100 ppt, move position center
	
	def dim():
		# create an empty window with title "dimmer"
		# when it's focused, first executes "swaymsg [workspace=__focused__ floating] kill", then closes itself
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.SwayShell", "Dim", "/ushell/SwayShell", None, Gio.DBusSignalFlags.NONE, dim)
	
	setup_bar(app)
	setup_launcher(app)
	setup_locker(app)
	setup_osk(app)
	
	setup_screens()
	setup_voice_control()
	
	# run uni.desktop
	
	# [ -e "$HOME"/.config/ushell/autostart ] && sh "$HOME"/.config/ushell/autostart

Gtk.Settings.get_default().props.gtk_overlay_scrolling = False

app = Gtk.Application(application_id='ushell.SwayShell')
app.connect('activate', on_activate)
app.run()
