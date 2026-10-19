from gi.repository import GLib as glib
from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def lock(ushell :gtk.Application):
	# if there is no window titled 'locker' in application's window list,
	# create a semi'transparent fullscreen layer showing a 10 seconds countdown
	# upon any input activity, or when unfocused, close the layer
	
	counter_window = gtk.Window(application=ushell, opacity=0.5)
	
	eventctl = gtk.EventControllerLegacy()
	eventctl.connect('event', lambda _: lock_window.close())
	lock_window.add_controller(eventctl)
	
	def on_timeout(timeout_source :glib.Source):
		timeout_source.destroy()
		# dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Lock
	
	timeout_source = glib.timeout_source_new_seconds(10)
	timeout_source.set_callback()
	timeout_source.attach(glib.MainContext.default())
	counter.connect('close_request', lambda: timeout_source.destroy())
	
	gls.init_for_window(lock_window)
	gls.set_layer(lock_window, gls.Layer.OVERLAY)
	gls.set_anchor(lock_window, gls.Edge.TOP, True)
	gls.set_anchor(lock_window, gls.Edge.BOTTOM, True)
	gls.set_anchor(lock_window, gls.Edge.LEFT, True)
	gls.set_anchor(lock_window, gls.Edge.RIGHT, True)
	gls.set_exclusive_zone(lock_window, -1)
	gls.set_keyboard_mode(lock_window, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(lock_window, True)
	
	lock_window.present()
	if not lock_window.contains_focus(): lock_window.close()
	
	# https://wiki.archlinux.org/title/Backlight
	# https://github.com/FedeDP/Clight/wiki/Modules#wayland-support
	# https://quickshell.org/docs/v0.1.0/types/Quickshell.Widgets/WrapperItem/
	# https://doc.qt.io/qt-6/qml-qtquick-effects-multieffect.html
	#
	# https://wiki.archlinux.org/title/Power_management
	# battery
	# power profiles (latency config) https://docs.kernel.org/power/pm_qos_interface.html
	# 	https://github.com/linrunner/TLP
	# https://github.com/Hummer12007/brightnessctl
	#
	# in modern systems, other hardwares (cpu, network ...) are automatically put into low consumption (high latency) mode,
	# 	unless an application specifically request for low latency using Linux PM QoS
	# 	https://docs.kernel.org/power/pm_qos_interface.html

def setup_locker(ushell :gtk.Application):
	bat_stat_path = '/sys/class/power_supply/BAT0/status'
	lock_cmd = 'dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Lock'
	
	gio.Subprocess(['swayidle', '-w',
		'timeout', '60', '[ -e {bat_stat_path} ] && [ $(cat {bat_stat_path}) = Discharging ] && {lock_cmd}',
		'timeout', '600', lock_cmd
	], gio.SubprocessFlags.NONE)
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Lock", "/ushell/Ushell", None, Gio.DBusSignalFlags.NONE, lambda: lock(ushell))
