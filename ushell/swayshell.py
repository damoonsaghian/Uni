import subprocess

# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
import ctypes
ctypes.CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Gio, Gdk, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from bar import setup_bar
from launcher import setup_launcher
from locker import setup_locker
from osk import setup_osk
from screens import setup_screens
from speech import speech

def on_startup(app):
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
	setup_screens(app)
	setup_speech(app)
	
	# run uni.desktop
	
	# [ -e "$HOME"/.config/ushell/autostart ] && sh "$HOME"/.config/ushell/autostart

Gtk.Settings.get_default().props.gtk_overlay_scrolling = False

app = Gtk.Application(application_id='ushell.SwayShell')
app.connect('activate', on_activate)
app.run()
