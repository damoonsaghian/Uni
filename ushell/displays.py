from gi.repository import Gio as gio
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def setup_display_windows(ushell :gtk.Application):
	# display windows: windows with title __ext__ or with specs mentioned in ~/.config/ushell/display-windows.json
	# specs: app_id/class, title
	
	def manage_display_windows():
		pass
		
		# display_windows_specs = '[{"title": "__ext__"}]'
		# extend this list with the list of specs mentioned in ~/.config/ushell/display-windows.json
		
		# get the list of windows, filter with display_windows_specs
		# move them to workspace 1 2 3 ...
		# turn on the corresponding outputs
		# turn off empty outputs (except the primary one)
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "ManageDisplayWindows", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		manage_display_windows
	)
	
	manage_display_windows_script = """
	{ swaymsg -m -t subscribe '["window"]' || swaynag -m "display windows manager failed"; } | while read _; do
		dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.ManageDisplayWindows
	done
	"""
	gio.Subprocess(['sh', '-c', manage_display_windows_script],	gio.SubprocessFlags.NONE)
	
	# when ~/.config/ushell/display-windows changes: manage_display_windows

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
	
	setup_display_windows(ushell)
	
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
