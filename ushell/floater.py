from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

# when the state of a window changes:
# if the focused window is tiling, kill all floating windows of current workspace,
# 	then if it's not the first window of workspace, make it floating
# if the focused window is floating, and there is no dimmer, open one
floater_script = """
{ swaymsg -m -t subscribe '["window"]' || swaynag -m "floater failed"; } | while read _; do
	if swaymsg "[con_id=__focused__ tiling] focus"; then
		swaymsg "[workspace=__focused__ floating] kill"
		swaymsg focus prev && swaymsg "focus next; floating enable"
	elif swaymsg "[con_id=__focused__ floating] focus" &&
		! swaymsg "[workspace=__focused__ app_id='ushell\.Ushell' title=dimmer] floating enable"
	then
		dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Dim
	fi
done
"""

def open_dimmer():
	# create an empty window with title "dimmer"
	# when it's focused, first executes "swaymsg [workspace=__focused__ floating] kill", then closes itself

def setup_floater(app :gtk.Application):
	gio.Subprocess(['sh', '-c', floater_script], gio.SubprocessFlags.NONE)
	
	gio.Subprocess(['swaymsg', 'no_focus [app_id="ushell.Ushell" title=dimmer]'], gio.SubprocessFlags.NONE)
	gio.Subprocess(['swaymsg',
		'for_window [app_id="ushell.Ushell" title=dimmer] opacity 0.5, floating enable, ' +
		'resize set 100 ppt 100 ppt, move position center'
	], gio.SubprocessFlags.NONE)
	
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Dim", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, open_dimmer)
