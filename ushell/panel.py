from gi.repository import Gio as gio
from gi.repository import GioUnix as giox
from gi.repository import Gtk as gtk
from gi.repository import Adw as adw
from gi.repository import Gtk4LayerShell as gls

from prompt import prompt_view
from system import system_view
from ..uni.menu import Menu

def swapp(app_id):
	swaywrap_script = f'swaymsg workspace "{app_id}"; swaymsg [con_id=__focused__] focus || gtk4-launch "{app_id}"'
	gio.Subprocess(['sh', '-c', swaywrap_script], gio.SubprocessFlags.NONE)

# model is made from prompt, system, and application's desktop files
# the factory produces widgets that:
# on pressing enter, or click/tap: self.app.launch
# right click (hold) on app entries -> show close button on open app icons, plus a close all button
# backspace or delete -> close selected app's appspace

def setup_lock(ushell :gtk.Application, main_view :gtk.Stack, naview :gtk.NavigationView):
	# if correct password is entered (su nu -c true): close password layer, swaymsg workspace lock
	# the password layer has a 60 sec (10 sec on battery) idle timer that will turn the screens off:
	# 	swaymsg "output - power off; seat - idle_inhibit keyboard pointer touchpad tablet_pad tablet_tool switch;"
	# 	anchor the panel's layer to all the edges of the screen
	# 	keyboard focus on panel window
	# upon any input activity, or if unfocused, or if power button is pressed, or when resume from suspend:
	# 	swaymsg "output - power on; seat - idle_inhibit keyboard pointer touchpad tablet_pad touch tablet_tool switch"
	# 	unanchor the panel's layer from top left and right edges
	# 	keyboard focus on passwrod entry
	
	# when password is entered correctly, set panel's layer to BOTTOM, show apps view
	
	# passwd_entry keybinding: escape -> close panel
	
	# double tap -> turn the screen on/off
	# gio.Subprocess(["swaymsg", "output - power on"], gio.SubprocessFlags.NONE)
	
	# on touch screen:
	# , if an unlock pattern is set, show pattern unlocking
	# , otherwise ask for password, and if no keyboard is connected, show virtual keyboard,
	# 	and after the password is entered correctly, ask user to set a pattern
	
	def lock():
		naview.set_visible_child_name('lock')
		swapp('uni.UniLock')
		for window in ushell.get_windows():
			if gls.is_layer_window(window):
				gls.set_layer(window, gls.Layer.OVERLAY)
	
	# start in locked mode
	lock()
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelLock", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, lock
	)
	
	def unlock():
		naview.set_visible_child_name('nav')
		gio.Subprocess(['swaymsg', 'workspace back_and_forth'], gio.SubprocessFlags.NONE)
	
	passwd_entry = gtk.PasswordEntry()
	passwd_entry.connect('activate', unlock)
	main_view.add_named(passwd_entry, 'lock')

	# use handle-power-key inhibitor lock to prevent system poweroff when pressing power button
	# and instead run lock()
	# https://systemd.io/INHIBITOR_LOCKS/
	# https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html
	# hook dirs are a hacky alternative:
	# 	https://manned.org/man/alpine-3.23/loginctl.1
	# 	https://manned.org/man/alpine-3.23/logind.conf.5

def setup_dim_layer():
	# used behind panel
	overlay_dim = gtk.Window(application=ushell, title='dim-layer', opacity=0.5)
	# the moment this window recieves a click/tap event, it hides itself, then hide_all()
	gls.init_for_window(overlay_dim)
	gls.set_layer(overlay_dim, gls.Layer.BACKGROUND)
	gls.set_anchor(overlay_dim, gls.Edge.LEFT, True)
	gls.set_anchor(overlay_dim, gls.Edge.RIGHT, True)
	gls.set_anchor(overlay_dim, gls.Edge.TOP, True)
	gls.set_anchor(overlay_dim, gls.Edge.BOTTOM, True)
	gls.set_keyboard_mode(overlay_dim, gls.KeyboardMode.NONE)
	gls.set_respect_close(overlay_dim, True)
	overlay_dim.present()

def setup_panel(ushell :gtk.Application):
	setup_dim_layer()
	
	window = gtk.Window(application=ushell)
	window.set_default_size(width=294, height=360)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.BOTTOM)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_margin(window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(window, gls.KeyboardMode.EXCLUSIVE)
	gls.set_respect_close(window, True)
	window.present()
	
	main_view = gtk.Stack()
	main_view.add_named(naview, 'nav')
	window.set_child(main_view)
	
	naview = adw.NavigationView()
	naview.add(
		gtk.NavigationPage(child=apps_view(), tag='apps')
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
	
	# gtk.ActionBar
	# two buttons at top
	# left: super prompt (press space)
	# right: system menu (press enter)
	
	# naview keybinding: escape -> close panel
	
	# implement an interface to close applications (delete key, right click, and long'press geature)
	
	# for apps in ~/.config/autostart/
	# autostart_app = giox.DesktopAppInfo.new_from_filename(path)
	# if autostrart_app: autostart_app.launch()
	
	swapp('uni.Uni')
	
	setup_lock(ushell, main_view, naview)
	
	def toggle_panel():
		# if apps page has focus, close panel and go to previous workspace
		# otherwise focus apps page
		if naview.get_visible_page().tag == 'apps':
			for window in ushell.get_windows():
				if gls.is_layer_window(window):
					if window.props.title == 'dim-layer':
						gls.set_layer(window, gls.Layer.BACKGROUND)
					else:
						gls.set_layer(window, gls.Layer.BOTTOM)
			gio.Subprocess(['swaymsg', 'workspace back_and_forth'], gio.SubprocessFlags.NONE)
		else:
			for window in ushell.get_windows():
				if gls.is_layer_window(window):
					gls.set_layer(window, gls.Layer.OVERLAY)
			naview.set_visible_child_name('apps')
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelToggle", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		toggle_panel
	)
