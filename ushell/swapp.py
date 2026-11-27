from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

current_app = "uni.Uni"
previous_app = "uni.Uni"

def swapp(app_id :str):
	global current_app, previous_app
	swaywrap_script = f'swaymsg workspace "{app_id}"; swaymsg [con_id=__focused__] focus || gtk4-launch "{app_id}"'
	
	# to protect system from autostart apps, run non'system apps in a bubblewrap sandbox
	# from gi.repository import GioUnix as giox
	# app_filename :str|None = giox.DesktopAppInfo.new(app_id).get_filename()
	# if it's a symlink, replace it with the real path
	# if app_filename basename is not "/usr/share/applications" or "/usr/local/share/applications", run it in sandbox
	
	gio.Subprocess(argv=['sh', '-c', swaywrap_script])
	previous_app = current_app
	current_app = app_id

def swapp_view():
	...
	# model is made from prompt, system, and application's desktop files
	# the factory produces widgets that:
	# on pressing enter, or click/tap: self.app.launch
	# right click (hold) on app entries -> show close button on open app icons, plus a close all button
	# backspace or delete -> close selected app's appspace
	
	# implement an interface to close applications (delete key, right click, and long'press geature)

def setup_swapp(ushell :gtk.Application):
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "SwappPrevious", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		lambda: gio.Subprocess(argv=['swaymsg', f'workspace {previous_app}'])
	)
	
	# for apps in ~/.config/autostart/
	# swapp(app_id)
	
	swapp('uni.Uni')
