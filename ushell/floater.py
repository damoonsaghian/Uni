from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

# when the state of a window changes:
# if the focused window is tiling, kill all floating windows of current workspace,
# 	then if it's not the first window of workspace, make it floating
# if the focused window is floating, and there is no dim-floater, open one
floater_script = """
{ swaymsg -m -t subscribe '["window"]' || swaynag -m "floater failed"; } | while read _; do
	if swaymsg "[con_id=__focused__ tiling] focus"; then
		swaymsg "[workspace=__focused__ floating] kill"
		swaymsg focus prev && swaymsg "focus next; floating enable"
	elif swaymsg "[con_id=__focused__ floating] focus" &&
		! swaymsg "[workspace=__focused__ app_id='ushell\.Ushell' title='dim-floater'] floating enable"
	then
		dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.DimFloater
	fi
done
"""

def open_dim_floater(ushell :gtk.Application):
	# create an empty window with title "dim-floater"
	# when it's focused, close all windows in current workspace	
	window = gtk.Window(application=ushell, title='dim-floater')
	focus_eventctl = gtk.EventControllerFocus()
	focus_eventctl.connect('enter', lambda: gio.Subprocess(
		['swaymsg', '[workspace=__focused__ floating] kill'], gio.SubprocessFlags.NONE
	))
	window.add_controller(focus_eventctl)
	window.present()

def setup_floater(ushell :gtk.Application):
	gio.Subprocess(['sh', '-c', floater_script], gio.SubprocessFlags.NONE)
	
	gio.Subprocess(['swaymsg', 'no_focus [app_id="ushell\.Ushell" title="dim-floater"]'], gio.SubprocessFlags.NONE)
	gio.Subprocess(['swaymsg',
		'for_window [app_id="ushell\.Ushell" title="dim-floater"] opacity 0.5, floating enable, ' +
		'resize set 100 ppt 100 ppt, move position center'
	], gio.SubprocessFlags.NONE)
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "DimFloater", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		lambda: open_dim_floater(ushell)
	)
