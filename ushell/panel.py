from gi.repository import GLib as glib
from gi.repository import Gio as gio
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk
from gi.repository import Adw as adw
from gi.repository import Gtk4LayerShell as gls

from .prompt import prompt_view
from .system import system_view
from .swapp import swapp, swapp_view, swapp_previous
from ..uni.menu import Menu

def close_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
				gls.set_layer(window, gls.Layer.BOTTOM)

def open_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
			gls.set_layer(window, gls.Layer.OVERLAY)

def setup_lock(ushell :gtk.Application, panel_window :gtk.Window, naview :gtk.NavigationView):
	passwd_entry = gtk.PasswordEntry(placeholder_text='password', show_peek_icon=True)
	passwd_page = gtk.NavigationPage(child=passwd_entry, tag='lock', can_pop=False)
	naview.add(passwd_page)
	
	def display_off():
		gio.Subprocess(argv=["swaymsg",	"output - power off"])
	def display_on():
		gio.Subprocess(argv=["swaymsg",	"output - power on"])
	
	# passwd_page has a 20 sec idle timeout that will turn off the screen
	# upon a key/button press, or if passwd_page does not have focus, turn on the screen
	timeout_id = 0
	def set_timeout(_ = None, event :gdk.Event|None = None):
		nonlocal timeout_id
		if timeout_id != 0: glib.source_remove(timeout_id)
		timeout_id = glib.timeout_add_seconds(20, display_off)
		match event:
			case gdk.EventType.BUTTON_PRESS | gdk.EventType.PAD_BUTTON_PRESS | gdk.EventType.KEY_PRESS:
				display_on()
	def focus_changed(passwd_page :gtk.NavigationPage, _):
		nonlocal timeout_id
		if passwd_page.props.has_focus:
			set_timeout()
		else:
			if timeout_id != 0: glib.source_remove(timeout_id)
			display_on()
	passwd_page.connect('notify::has_focus', focus_changed)
	eventctl = gtk.EventControllerLegacy()
	eventctl.connect('event', set_timeout)
	passwd_page.add_controller(eventctl)
	
	# double tap/click on passwd_page to turn the screen on/off
	clickctl = gtk.GestureClick()
	def on_press(clickctl :gtk.GestureClick, n_clicks :int, _x, _y):
		clickctl.set_state(gtk.EventSequenceState.CLAIMED)
		if n_clicks == 2:
			gio.Subprocess(argv=["swaymsg",	"output - power toggle"])
	clickctl.connect('pressed', on_press)
	passwd_page.add_controller(clickctl)
	
	# on wakeup from suspend, call screen_on
	def dbus_proxy_callback(_object, result :gio.AsyncResult, _data):
		dbus_proxy = gio.DBusProxy.new_for_bus_finish(result)
		def sleep_handler(_dbus_proxy, _sender_name, _signal_name, parameters: glib.Variant):
			# if we are after suspend, turn on the display
			try:
				if not parameters.get_boolean(): display_on()
			except:
				display_on()
		dbus_proxy.connect('g-signal::PrepareForSleep', sleep_handler)
	
	gio.DBusProxy.new_for_bus(
		gio.BusType.SYSTEM,
		gio.DBusProxyFlags.NONE,
		None,
		"org.freedesktop.login1",
		"/org/freedesktop/login1",
		"org.freedesktop.login1.Manager",
		None,
		dbus_proxy_callback
	)
	
	def lock():
		naview.set_visible_child_name('lock')
		swapp('uni.UniLock')
		open_panel(ushell)
		passwd_entry.delete_text(0,-1)
	
	# start in locked mode
	lock()
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelLock", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, lock
	)
	
	def unlock(passwd_entry :gtk.PasswordEntry):
		def unlock_finish(subprocess :gio.Subprocess, _result, _data):
			if subprocess.get_exit_status() == 0:
				close_panel(ushell)
				naview.set_visible_child_name('apps')
				gio.Subprocess(argv=['swaymsg', 'workspace back_and_forth'])
			passwd_entry.props.editable = True
		
		passwd_entry.props.editable = False
		
		gio.Subprocess(
			argv=['sh', '-c', f'echo {passwd_entry.get_text()} | su nu -c true'],
			flags=gio.SubprocessFlags.STDOUT_SILENCE
		).wait_async(callback=unlock_finish)
	
	passwd_entry.connect('activate', unlock)
	
	def handle_power_key():
		if panel_window.props.title == "lock-layer":
			display_on()
			panel_window.props.title == ""
		else:
			lock()
			panel_window.props.title = "lock-layer"  # this also prevents the idle-manager from opening a counter layer
			display_off()
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelPowerKey", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, handle_power_key
	)

def setup_panel(ushell :gtk.Application):
	panel_window = gtk.Window(application=ushell)
	
	gls.init_for_window(panel_window)
	gls.set_layer(panel_window, gls.Layer.BOTTOM)
	gls.set_anchor(panel_window, gls.Edge.TOP, True)
	gls.set_anchor(panel_window, gls.Edge.BOTTOM, True)
	gls.set_anchor(panel_window, gls.Edge.LEFT, True)
	gls.set_anchor(panel_window, gls.Edge.RIGHT, True)
	gls.set_margin(panel_window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(panel_window, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(panel_window, True)
	panel_window.present()
	
	naview = adw.NavigationView()
	panel_window.set_child(naview)
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "SwappPrevious", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		swapp_previous
	)
	
	naview.add(
		gtk.NavigationPage(child=swapp_view(), tag='swapp', can_pop=False)
	)
	
	
	naview.add(
		gtk.NavigationPage(child=prompt_view(), tag='prompt')
	)
	
	naview.add(
		gtk.NavigationPage(child=system_view(), tag='system')
	)
	
	# naview keybinding: escape -> close panel
	
	# for apps in ~/.config/autostart/
	# swapp(app_id)
	
	swapp('uni.Uni')
	
	setup_lock(ushell, panel_window, naview)
	
	def toggle_panel():
		# if swapp or lock page has focus, close panel
		# otherwise open the panel and focus swapp page
		panel_page :str = naview.get_visible_page().tag
		if panel_page == 'swapp' or panel_page == 'lock':
			close_panel(ushell)
		else:
			open_panel(ushell)
			naview.set_visible_child_name('swapp')
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelToggle", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		toggle_panel
	)
