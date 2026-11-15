from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Adw as adw
from gi.repository import Gtk4LayerShell as gls

from .prompt import prompt_view
from .system import system_view
from ..uni.menu import Menu

def swapp(app_id):
	swaywrap_script = f'swaymsg workspace "{app_id}"; swaymsg [con_id=__focused__] focus || gtk4-launch "{app_id}"'
	gio.Subprocess(argv=['sh', '-c', swaywrap_script])

def close_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
			if window.props.title == 'dim-layer':
				gls.set_layer(window, gls.Layer.BACKGROUND)
			else:
				gls.set_layer(window, gls.Layer.BOTTOM)

def open_panel(ushell :gtk.Application):
	for window in ushell.get_windows():
		if gls.is_layer_window(window):
			gls.set_layer(window, gls.Layer.OVERLAY)

def setup_dim_layer(ushell :gtk.Application):	
	# used behind the panel
	# the moment this window recieves a click/tap event, it closes panel
	dim_window = gtk.Window(application=ushell, title='dim-layer', opacity=0.5)
	click_evctl = gtk.GestureClick(button=0) # listen for any button
	click_evctl.connect('released', lambda _n, _x, _y: close_panel(ushell))
	dim_window.add_controller(click_evctl)
	
	gls.init_for_window(dim_window)
	gls.set_layer(dim_window, gls.Layer.BACKGROUND)
	gls.set_anchor(dim_window, gls.Edge.LEFT, True)
	gls.set_anchor(dim_window, gls.Edge.RIGHT, True)
	gls.set_anchor(dim_window, gls.Edge.TOP, True)
	gls.set_anchor(dim_window, gls.Edge.BOTTOM, True)
	gls.set_keyboard_mode(dim_window, gls.KeyboardMode.NONE)
	gls.set_respect_close(dim_window, True)
	dim_window.present()

def setup_lock(ushell :gtk.Application, naview :gtk.NavigationView):
	passwd_entry = gtk.PasswordEntry(placeholder_text='password', show_peek_icon=True)
	passwd_page = gtk.NavigationPage(child=passwd_entry, tag='lock', can_pop=False)
	naview.add(passwd_page)
	
	# on touch screen:
	# , if an unlock pattern is set, show pattern unlocking instead
	# , otherwise ask for password, and after the password is entered correctly, ask user to set a pattern
	
	# the password layer has a 60 sec (10 sec on battery) idle timer that will turn the screens off:
	# 	swaymsg "output - power off; seat - idle_inhibit keyboard pointer touchpad tablet_pad tablet_tool switch;"
	# 	anchor the panel's layer to all the edges of the screen
	# 	keyboard focus on panel window
	# upon any input activity (including pressing power button), or if unfocused, or when resume from suspend:
	# 	swaymsg "output - power on; seat - idle_inhibit keyboard pointer touchpad tablet_pad touch tablet_tool switch"
	# 	unanchor the panel's layer from top left and right edges
	# 	keyboard focus on passwrod entry
	#
	# double tap -> turn the screen on/off
	# gio.Subprocess(argv=["swaymsg", "output - power on"])
	
	def lock():
		naview.set_visible_child_name('lock')
		swapp('uni.UniLock')
		open_panel(ushell)
	
	# start in locked mode
	lock()
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelLock", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, lock
	)
	
	def unlock():
		def unlock_finish():
			close_panel(ushell)
			naview.set_visible_child_name('apps')
			gio.Subprocess(argv=['swaymsg', 'workspace back_and_forth'])
			# unblock passed_entry input
		
		gio.Subprocess(
			argv=['sh', '-c', f'echo {passwd_entry.get_text()} | su nu -c true'],
			flags=gio.SubprocessFlags.STDOUT_SILENCE
		).communicate_async(callback=unlock_finish)
		
		# block passwd_enry input
	
	passwd_entry.connect('activate', unlock)
	
	# use handle-power-key inhibitor lock to prevent system poweroff when pressing power button
	# and instead run lock()
	# https://systemd.io/INHIBITOR_LOCKS/
	# https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html
	# hook dirs are a hacky alternative:
	# 	https://manned.org/man/alpine-3.23/loginctl.1
	# 	https://manned.org/man/alpine-3.23/logind.conf.5

def setup_panel(ushell :gtk.Application):
	setup_dim_layer(ushell)
	
	window = gtk.Window(application=ushell)
	window.set_default_size(width=294, height=360)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.BOTTOM)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_margin(window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(window, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(window, True)
	window.present()
	
	naview = adw.NavigationView()
	window.set_child(naview)
	
	naview.add(
		gtk.NavigationPage(child=apps_view(), tag='apps', can_pop=False)
	)
	
	# adw.Clamp
	
	# when naview is focused go to apps view
	naview.connect('focused', naview.set_visible_child_name('apps'))
	
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
	
	setup_lock(ushell, naview)
	
	def toggle_panel():
		# if apps page has focus, close panel and go to previous workspace
		# otherwise if lock page has focus, close panel
		# otherwise open the panel and focus apps page
		if naview.get_visible_page().tag == 'apps':
			close_panel()
			gio.Subprocess(argv=['swaymsg', 'workspace back_and_forth'])
		elif naview.get_visible_page().tag == 'lock'
			close_panel()
		else:
			open_panel(ushell)
			naview.set_visible_child_name('apps')
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelToggle", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		toggle_panel
	)
