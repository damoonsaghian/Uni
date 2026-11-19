from gi.repository import GLib as glib
from gi.repository import Gio as gio
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk
from gi.repository import Adw as adw
from gi.repository import Gtk4LayerShell as gls

from .prompt import prompt_view
from .system import system_view
from ..uni.menu import Menu

current_app = "uni.Uni"
previous_app = "uni.Uni"

def swapp(app_id :str):
	global current_app, previous_app
	swaywrap_script = f'swaymsg workspace "{app_id}"; swaymsg [con_id=__focused__] focus || gtk4-launch "{app_id}"'
	gio.Subprocess(argv=['sh', '-c', swaywrap_script])
	if app_id != 'uni.UniLock':
		previous_app = current_app
		current_app = app_id

def close_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
				gls.set_layer(window, gls.Layer.BOTTOM)

def open_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
			gls.set_layer(window, gls.Layer.OVERLAY)

def setup_dim_layer(ushell :gtk.Application):
	dim_window = gtk.Window(application=ushell, title='dim-layer', opacity=0.5)
	click_evctl = gtk.GestureClick(button=0)  # listen for any button
	click_evctl.connect('released', lambda *_: close_panel(ushell))
	dim_window.add_controller(click_evctl)
	
	gls.init_for_window(dim_window)
	gls.set_layer(dim_window, gls.Layer.BOTTOM)
	gls.set_anchor(dim_window, gls.Edge.LEFT, True)
	gls.set_anchor(dim_window, gls.Edge.RIGHT, True)
	gls.set_anchor(dim_window, gls.Edge.TOP, True)
	gls.set_anchor(dim_window, gls.Edge.BOTTOM, True)
	gls.set_keyboard_mode(dim_window, gls.KeyboardMode.NONE)
	gls.set_respect_close(dim_window, True)
	dim_window.present()

def setup_lock(ushell :gtk.Application, panel_window :gtk.Window, naview :gtk.NavigationView):
	passwd_entry = gtk.PasswordEntry(placeholder_text='password', show_peek_icon=True)
	passwd_page = gtk.NavigationPage(child=passwd_entry, tag='lock', can_pop=False)
	naview.add(passwd_page)
	
	# passwd_page has a 20 sec idle timeout that will turn off the screen
	# upon a key/button press, or if passwd_page does not have focus, turn on the screen
	def display_off():
		gio.Subprocess(argv=["swaymsg",	"output - power off"])
		# to capture pointer/touch, anchor panel_window to all edges
		gls.set_anchor(panel_window, gls.Edge.TOP, True)
		gls.set_anchor(panel_window, gls.Edge.BOTTOM, True)
		gls.set_anchor(panel_window, gls.Edge.LEFT, True)
		gls.set_anchor(panel_window, gls.Edge.RIGHT, True)
		panel_window.props.title = "lock-layer"  # to prevent the idle-manager from opening a counter layer
		passwd_entry.props.editable = False
	def display_on():
		gio.Subprocess(argv=["swaymsg",	"output - power on"])
		gls.set_anchor(panel_window, gls.Edge.TOP, False)
		gls.set_anchor(panel_window, gls.Edge.BOTTOM, True)
		gls.set_anchor(panel_window, gls.Edge.LEFT, False)
		gls.set_anchor(panel_window, gls.Edge.RIGHT, False)
		panel_window.props.title = ""
		passwd_entry.props.editable = True
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
	
	# when resume from suspend, screen_on
	
	# double tap -> turn the screen on/off
	
	def lock():
		naview.set_visible_child_name('lock')
		swapp('uni.UniLock')
		open_panel(ushell)
	
	# start in locked mode
	lock()
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelLock", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, lock
	)
	
	def unlock(passwd_entry :gtk.PasswordEntry):
		def unlock_finish():
			close_panel(ushell)
			naview.set_visible_child_name('apps')
			gio.Subprocess(argv=['swaymsg', 'workspace back_and_forth'])
			# unblock passwd_entry input
		
		gio.Subprocess(
			argv=['sh', '-c', f'echo {passwd_entry.get_text()} | su nu -c true'],
			flags=gio.SubprocessFlags.STDOUT_SILENCE
		).communicate_async(callback=unlock_finish)
	
	passwd_entry.connect('activate', unlock)
	
	# use handle-power-key inhibitor lock to prevent system poweroff when pressing power button
	# and instead run lock() and display_on/display_off
	# https://systemd.io/INHIBITOR_LOCKS/
	# https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html
	# hook dirs are a hacky alternative:
	# 	https://manned.org/man/alpine-3.23/loginctl.1
	# 	https://manned.org/man/alpine-3.23/logind.conf.5

def setup_panel(ushell :gtk.Application):
	setup_dim_layer(ushell)
	
	panel_window = gtk.Window(application=ushell)
	panel_window.set_default_size(width=294, height=360)
	
	gls.init_for_window(panel_window)
	gls.set_layer(panel_window, gls.Layer.BOTTOM)
	gls.set_anchor(panel_window, gls.Edge.BOTTOM, True)
	gls.set_margin(panel_window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(panel_window, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(panel_window, True)
	panel_window.present()
	
	naview = adw.NavigationView()
	panel_window.set_child(naview)
	
	naview.add(
		gtk.NavigationPage(child=apps_view(), tag='apps', can_pop=False)
	)
	
	# adw.Clamp
	
	naview.add(
		gtk.NavigationPage(child=prompt_view(), tag='prompt')
	)
	
	naview.add(
		gtk.NavigationPage(child=system_view(), tag='system')
	)
	
	# model is made from prompt, system, and application's desktop files
	# the factory produces widgets that:
	# on pressing enter, or click/tap: self.app.launch
	# right click (hold) on app entries -> show close button on open app icons, plus a close all button
	# backspace or delete -> close selected app's appspace
	
	# gtk.ActionBar
	# two buttons at top
	# left: super prompt (press space)
	# right: system menu (press enter)
	
	# naview keybinding: escape -> close panel
	
	# implement an interface to close applications (delete key, right click, and long'press geature)
	
	# for apps in ~/.config/autostart/
	# swapp(app_id)
	
	swapp('uni.Uni')
	
	setup_lock(ushell, panel_window, naview)
	
	def toggle_panel():
		# if apps page has focus, close panel and go to previous app
		# otherwise if lock page has focus, close panel
		# otherwise open the panel and focus apps page
		if naview.get_visible_page().tag == 'apps':
			close_panel()
			gio.Subprocess(argv=['swaymsg', f'workspace {previous_app}'])
		elif naview.get_visible_page().tag == 'lock'
			close_panel()
		else:
			open_panel(ushell)
			naview.set_visible_child_name('apps')
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelToggle", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		toggle_panel
	)
