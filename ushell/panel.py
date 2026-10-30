from gi.repository import Gio as gio
from gi.repository import GioUnix as giox
from gi.repository import Gtk as gtk
from gi.repository import Adw as adw
from gi.repository import Gtk4LayerShell as gls

from prompt import prompt_view
from system import system_view
from termulator import termulator

class SwayApp(giox.DesktopAppInfo):
	# run apps inside a bwrap sandbox that blocks sway's socket,
	# 	and protects wayland socket using wayland security context
	# this prevents a malicious program from stealing root password, by faking password entry
	# https://niri-wm.github.io/niri/Security-Model.html
	# so using sudo in Ushell does not suffer from these flaws:
	# https://www.reddit.com/r/linuxquestions/comments/8mlil7/whats_the_point_of_the_sudo_password_prompt_if/
	# https://security.stackexchange.com/questions/119410/why-should-one-use-sudo
	def do_launch(self):
		swaywrap_script = f"""
		# if file $HOME/.config/ushell/autostart/<workspace-name> exists (containg output-num):
		# swaymsg move workspace to output-num
		swaymsg [con_id=__focused__] focus ||
		bwrap --bind / / --bind /dev/null "$SWAYSOCK" \
			--bind "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"-sandbox "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
			--bind /dev/null /usr/bin/lisgd \
			-- gtk4-launch "{self.get_id()}"
		"""
		gio.Subprocess(['sh', '-c', swaywrap_script], gio.SubprocessFlags.NONE)
	
	# when an app "StartupNotify=true" in its .destop file is selected by holding space for 2 seconds,
		# one of the context menu entries is "autostart"
	# it asks for a display number starting from 2
	# then makes a symbolic link in: $HOME/.config/ushell/autostart/"$display_num"
	# self.launch()
	# swaymsg "move workspace to $output_name; workspace back_and_forth"

class Item(gtk.Widget):
	def __init__(self, app :SwayApp):
		self = gtk.Widget()
		self.app = app
		
		# on pressing enter, or click/tap: self.app.launch
		
		# right click (hold) on app entries -> show close button on open app icons, plus a close all button
		# backspace or delete -> close selected app's appspace

class ItemList(gtk.Widget):
	def __init__(self):
		self.apps_list :List[SwayApp] = []
		# adw.Clamp
		
		# FlowBox containing apps
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.AUTOMATIC)
		flowbox = gtk.FlowBox()
		flowbox.set_margin_top(12)
		flowbox.set_margin_end(12)
		flowbox.set_margin_bottom(12)
		flowbox.set_margin_start(12)
		flowbox.set_valign(gtk.Align.START)
		flowbox.set_max_children_per_line(5)
		flowbox.set_selection_mode(gtk.SelectionMode.NONE)
		scrolled_window.set_child(flowbox)
		# flowbox.insert(widget)
		# flowbox.append(app_entry)

	# for all items, determine those characters in their names, that are enough to reach them
	# and slightly highlight them
	
	# self.selected_item = self.apps_list.get_item(0)
	# flowbox_child = self.apps_flowbox.get_child_at_index(0)
	# if flowbox_child:
	# 	self.apps_flowbox.select_child(flowbox_child)
	
	# re.compile(search_pattern).match(item.get_name()):
	# self.selected_item = item
	# flowbox_child = self.apps_flowbox.get_child_at_index(i)
	# if flowbox_child: self.apps_flowbox.select_child(flowbox_child)
	
	# app_item = self.selected_item
	# app_name = app_item.get_name()
	# gio.Subprocess([
	# 	'swaymsg',
	# 	f'[app_id=codev] move workspace {app_name}; workspace {app_name}'
	# ], gio.SubprocessFlags.NONE)
	# if not gio.Subprocess(['swaymsg', '[floating] focus'], gio.SubprocessFlags.NONE):
	# 	gio.Subprocess(['swaymsg', 'exec ' + app_item.get_executable()], gio.SubprocessFlags.NONE)
	
	# notify:has-focus: select system
	
	# app list is a flowbox whose model is a list store that will be updated when .desktop files of apps changes
	def compare_apps(self, app1 :gio.AppInfo, app2 :gio.AppInfo):
		app1_name = app1.get_name()
		app2_name = app2.get_name()
		if app2_name > app1_name:
			return -1
		if app1_name > app2_name:
			return 1
		return 0
	def update_apps_list(self):
		self.apps_list.remove_all()
		for app in gio.AppInfo.get_all():
			if app.should_show():
				self.apps_list.insert_sorted(app, self.compare_apps)
		settings_app = gio.AppInfo.create_from_commandline("settings")
		self.apps_list.insert(0, settings_app)
	def create_widget(self, app_item :gio.AppInfo):
		app_name = app_item.get_name()
		label = gtk.Label(
			label = app_name,
			justify = gtk.Justification.CENTER,
			width_chars = 20
		)
		icon = app_item.get_icon()
		if not icon:
			if app_name == "settings":
				icon = gio.ThemedIcon("applications-system-symbolic")
			else:
				icon = gio.ThemedIcon("")
		icon_image = gtk.Image.new_from_gicon(icon)
		widget = gtk.Box(orientation = gtk.Orientation.VERTICAL, spacing = 5)
		widget.append(icon_image)
		widget.append(label)
		return widget
	# the first element is selected by default
	# when an item in the flowbox is clicked, run the app
	# 	selected_child :gtk.FlowBoxChild = apps_flowbox.get_selected_children()[0]
	# 	index = selected_child.get_index()
	# 	self.selected_item = self.apps_list.get_item(index)
	# 	self.on_activate()

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
		SwayApp.new('uni.UniLock').launch()
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
		# https://manned.org/man/alpine-3.23/loginctl.1
		# https://manned.org/man/alpine-3.23/logind.conf.5

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
		gtk.NavigationPage(child=apps_list, tag='home')
	)
	
	# when naview is focused go to home
	naview.connect('focused', naview.set_visible_child_name('home'))
	
	# gtk.ActionBar
	# two buttons at top
	# left: super prompt (press any punctuation key ';,.)
	# right: system menu (selected by default)
	
	# naview keybinding: escape -> close panel
	
	# page with application items plus terminal item, with prompt and system on top actionbar
	# terminal item activation: open_termulator(naview)
	naview.add(
		gtk.NavigationPage(child=termulator(), tag='termulator')
	)
	
	# implement an interface to select and close applications (keyboard and long'press gesture)
	
	# autostart
	# for each $HOME/.config/ushell/autostart/$app_id (contaning output-num), if there is an output:
		# create a SwayApp and launch it
		# swaymsg "move workspace to $output_name"
	# swaymsg "workspace 1"
	# turn off empty outputs (except the primary one)
	
	# swaymsg -t workspace subscribe
	# when workspace changes, if this is not the primary output: move workspace to $primary_output
	
	SwayApp.new('uni.Uni.desktop').launch()
	# monitor dbus connection at uni.Uni, and when it's closed, relaunch Uni
	
	setup_lock(ushell, main_view, naview)
	
	def toggle_panel():
		# if apps page has focus, close panel and go to previous workspace
		# otherwise focus apps page
		if naview.get_visible_page().tag == 'home':
			for window in ushell.get_windows():
				if gls.is_layer_window(window):
					if window.props.title == 'dim-layer':
						gls.set_layer(window, gls.Layer.BACKGROUND)
					else:
						gls.set_layer(window, gls.Layer.BOTTOM)
			# if file $HOME/.config/ushell/autostart/<workspace-name> exists (containg output-num):
			# swaymsg move workspace to output-num
			gio.Subprocess(['swaymsg', 'workspace back_and_forth'], gio.SubprocessFlags.NONE)
		else:
			for window in ushell.get_windows():
				if gls.is_layer_window(window):
					gls.set_layer(window, gls.Layer.OVERLAY)
			naview.set_visible_child_name('home')
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "PanelToggle", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		toggle_panel
	)
