from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

current_app = "uni.Uni"
previous_app = "uni.Uni"

def swapp(app_id :str):
	global current_app, previous_app
	swaywrap_script = f'swaymsg workspace "{app_id}"; swaymsg [con_id=__focused__] focus || gtk4-launch "{app_id}"'
	
	gio.Subprocess(argv=['sh', '-c', swaywrap_script])
	previous_app = current_app
	current_app = app_id

def swapp_view():
	...
	# model is made from prompt, system, and application's desktop files
	# the factory produces widgets that:
	
	# item activate: self.app.launch
	
	# context buttons:
	# close button (shortcut: delete)
	# autostart button: gio.Subprocess(argv=['ushell-autostart', app_id])

def setup_swapp(ushell :gtk.Application):
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "SwappPrevious", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		lambda: gio.Subprocess(argv=['swaymsg', f'workspace {previous_app}'])
	)
	
	# for apps in ~/.config/autostart/
	# swapp(app_id)
	
	swapp('uni.Uni')
