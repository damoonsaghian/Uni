from gi.repository import GLib as glib
from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def idle_countdown(ushell :gtk.Application):
	# if there already is a lock-countdown, do nothing
	for window in ushell.get_windows():
		if window.props.title == 'lock-countdown': return
	
	# create a semi'transparent fullscreen layer showing a 10 seconds countdown
	# upon any input activity, or when unfocused, close the layer
	# when countdown is finished, close the layer, and lock Ushell
	
	countdown_win = gtk.Window(application=ushell, opacity=0.5, title='lock-countdown')
	
	eventctl = gtk.EventControllerLegacy()
	eventctl.connect('event', lambda _: countdown_win.close())
	countdown_win.add_controller(eventctl)
	
	countdown_label = gtk.Label(halign=gtk.Align.CENTER, valign=gtk.Align.CENTER)
	countdown_win.set_child(countdown_label)
	
	countdown = 10
	
	def on_timeout(countdown :int):
		countdown = countdown - 1
		countdown_label.set_label(f'<span size="xx-large" weight="bold">{str(countdown)}</span>')
		if countdown == 0:
			gio.Subprocess(
				['dbus-send', '--dest=ushell.Ushell', '/ushell/Ushell', 'ushell.Ushell.Lock'],
				gio.SubprocessFlags.NONE
			)
			countdown_win.close()
	timeout_id = timeout_add_seconds(1, lambda: on_timeout(countdown))
	countdown_win.connect('close_request', lambda: glib.source_remove(timeout_id))
	
	gls.init_for_window(countdown_win)
	gls.set_layer(countdown_win, gls.Layer.OVERLAY)
	gls.set_anchor(countdown_win, gls.Edge.TOP, True)
	gls.set_anchor(countdown_win, gls.Edge.BOTTOM, True)
	gls.set_anchor(countdown_win, gls.Edge.LEFT, True)
	gls.set_anchor(countdown_win, gls.Edge.RIGHT, True)
	gls.set_exclusive_zone(countdown_win, -1)
	gls.set_keyboard_mode(countdown_win, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(countdown_win, True)
	
	countdown_win.present()

def setup_idle_manager(ushell :gtk.Application):
	bat_stat_path = '/sys/class/power_supply/BAT0/status'
	countdown_cmd = 'dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.IdleCountdown'
	
	gio.Subprocess(['swayidle', '-w',
		'timeout', '60', '[ -e {bat_stat_path} ] && [ $(cat {bat_stat_path}) = Discharging ] && {countdown_cmd}',
		'timeout', '600', countdown_cmd
	], gio.SubprocessFlags.NONE)
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "IdleCountdown", "/ushell/Ushell", None, Gio.DBusSignalFlags.NONE,
		lambda: idle_countdown(ushell)
	)
