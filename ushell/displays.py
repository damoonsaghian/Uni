from gi.repository import Gio as gio
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def setup_displays(ushell :gtk.Application):
	# when monitors are added/removed:
	# , move ushell's layer'windows to primary output: gls.set_monitor(gtkwindow, gdkmonitor)
	# , move the focused workspace to the primary output (output 0), and turn it on
	# , move workspace 1 ... to output 1 ..., and turn it on
	# this way, the first monitor will always remains the main monitor, even after reconnecting
	# display = gdk.Display.get_default()
	# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
	# https://docs.gtk.org/gdk4/class.Monitor.html
	# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
	# https://github.com/tamirzb/qkdisplays
	
	# turn off empty outputs (except the primary one)
	
	# when window is removed from a numeric workspace, turn the display off
	
	# display windows: windows with title ' ' or with specs mentioned in ~/.config/ushell/display-windows
	# specs: app_id/class title
	def make_display_window():
		pass
		# find the first empty numeric workspace (try to disable floating; if it fails, then workspace is empty)
		# move the window to the workspace
		# turn on the corresponding output
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Displays", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		make_display_window
	)
	display_windows_spec = 'title="^ $"'
	gio.Subprocess([
		'swaymsg',
		f'for_window [{display_windows_spec}] exec dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Displays'
	], gio.SubprocessFlags.NONE)
	
	# if display is landscape: width=80 height=80 pos="center"
	# if display is portrait: width=100 height=80 pos="0 ppt 20 ppt"
	ws=".*"
	width="80"
	height="80"
	pos="center"
	gio.Subprocess(
		["swaymsg", f"for_window [workspace={ws} floating] resize set {width} ppt {height} ppt; move position {pos}"],
		gio.SubprocessFlags.NONE
	)
