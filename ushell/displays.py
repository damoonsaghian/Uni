from gi.repository import Gio as gio
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def setup_displays(app :gtk.Application):
	# when monitors are added/removed:
	# , move app's windows (bar and launcher) to first output: gls.set_monitor(gtkwindow, gdkmonitor)
	# , take the list of workspaces (using swaymsg)
	# , move the first non'numeric workspace to the first output (and turn it on)
	# , move workspace 2 ... to output 2 ...
	# this way, the first monitor will always remains the main monitor, even after reconnecting
	# display = gdk.Display.get_default()
	# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
	# https://docs.gtk.org/gdk4/class.Monitor.html
	# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
	# https://github.com/tamirzb/qkdisplays
	
	# run comands in ~/.config/ushell/displays using swaymsg
	# focus the first monitor
	# turn off empty outputs (except the primary one)
	
	# [ -e "$HOME"/.config/ushell/autostart ] && sh "$HOME"/.config/ushell/autostart
	
	# if display is landscape: width=80 height=80 pos="center"
	# if display is portrait: width=100 height=80 pos="0 ppt 20 ppt"
	# ["swaymsg", f"for_window [floating workspace={num}] resize set {width} ppt {haight} ppt; move position {pos}"]
	
	gio.Subprocess(["swaymsg", "bindswitch lid:on output - disable"], gio.SubprocessFlags.NONE)
	gio.Subprocess(["swaymsg", "bindswitch lid:off output * enable"], gio.SubprocessFlags.NONE)
