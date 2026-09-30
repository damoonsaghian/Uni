import subprocess

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

def setup_dimmer(app :gtk.Application):
	# when the state of a window changes:
	# if the focused window is tiling, kill all floating windows of current workspace,
	# 	then if it's not the first window of workspace, make it floating
	# if the focused window is floating, and there is no dimmer, open one
	subprocess.run("""
	{ swaymsg -m -t subscribe '["window"]' || swaynag -m "floater failed"; } | while read _; do
		if swaymsg "[con_id=__focused__ tiling] focus"; then
			swaymsg "[workspace=__focused__ floating] kill"
			swaymsg focus prev && swaymsg "focus next; floating enable"
		elif swaymsg "[con_id=__focused__ floating] focus" &&
			! swaymsg "[workspace=__focused__ app_id="ushell.Ushell" title=dimmer] floating enable"
		then
			dbus-send --dest=ushell.SwayShell /ushell/SwayShell ushell.Ushell.Dim
		fi
	done
	""", shell=True)
	
	subprocess.run(['swaymsg', 'no_focus [app_id="ushell.Ushell" title=dimmer]'])
	subprocess.run(['swaymsg',
		'for_window [app_id="ushell.Ushell" title=dimmer] opacity 0.5, floating enable, ' +
		'resize set 100 ppt 100 ppt, move position center'
	])
	
	def dim():
		# create an empty window with title "dimmer"
		# when it's focused, first executes "swaymsg [workspace=__focused__ floating] kill", then closes itself
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Dim", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, dim)