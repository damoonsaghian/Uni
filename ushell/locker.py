from gi.repository import GLib, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

def setup_locker(app :Gtk.Application):
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.SwayShell", "Lock", "/ushell/SwayShell", None, Gio.DBusSignalFlags.NONE, lock)
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.SwayShell", "LockIfBattery", "/ushell/SwayShell", None, Gio.DBusSignalFlags.NONE, lock_if_battery)

def lock_if_battery():
	#

def lock():
	# create a blury fullscreen layer showing a 10 seconds countdown
	# upon any input activity, or when unfocused, close the layer
	# after 10 seconds:
	# , swaymsg 'workspace lock'
	# , show password layer, with a transparent window, the size of the screen
	# password layer can be closed by pressing escape, or clicking outside of the entry box
	# when password layer is closed, and the workspace is empty (ie "swaymsg focus" fails), run: uni lock
	# if correct password is entered (check using su): close password layer, swaymsg workspace lock
	# the password layer has a 60 sec (10 sec on battery) idle timer that will turn the screens off:
	# 	swaymsg "output - power off; seat - idle_inhibit keyboard pointer touchpad tablet_pad tablet_tool switch; mode screen_off"
	# upon any input activity, or if unfocused, or resume from suspend:
	# 	swaymsg "output - power on; seat - idle_inhibit keyboard pointer touchpad tablet_pad touch tablet_tool switch"
	
	# lock
	# switch to workspace lock, and if workspace is empty, run: uni lock
	# super, alt+tab or click on statusbar: toggle password prompt
	# password prompt closes (showing  in lock mode) when Escape is pressed,
	# 	or when empty password is entered, or simply when password prompt is unfocused
	# start in locked mode
	# lock after 10m idle, if lock inhibit is not active
	# before lock, show a 10s countdown screen
	#
	# check for the password of user "nu":
	# su nu -c true
	#
	# plugged in: lock after 10 min idle, turn off display after 15 min idle
	# battery: decrease brightness after 5 min idle, lock after 10 min idle, turn off display after 11 min idle
	# low battery: decrease brightness after 2 min idle, lock and turn off display after 4 min idle,
	# 	suspend after 5 min idle
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
	# 30s idle after lock, poweroff screen
	# in modern systems, other hardwares (cpu, network ...) are automatically put into low consumption (high latency) mode,
	# 	unless an application specifically request for low latency using Linux PM QoS
	# 	https://docs.kernel.org/power/pm_qos_interface.html
	#
	# lock before suspend: https://systemd.io/INHIBITOR_LOCKS/
	
	# on touch screen:
	# , if an unlock pattern is set, show pattern unlocking
	# , otherwise ask for password, and if no keyboard is connected, show virtual keyboard,
	# 	and after the password is entered correctly, ask user to set a pattern
