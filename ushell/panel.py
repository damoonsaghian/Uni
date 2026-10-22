from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

from prompt import prompt_view
from system import system_view

def launch(app_name :str):
	swaywrap_script = f"""
	swaymsg workspace "{app_name}"
	swaymsg [con_id=__focused__] focus ||
	bwrap --bind / / --bind /dev/null "$SWAYSOCK" \
		--bind "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"-sandbox "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
		--bind /dev/null /usr/bin/lisgd \
		--bind /dev/null "$HOME/.config/ushell/screens" \
		--bind /dev/null "$HOME/.config/ushell/autostart" \
		-- gtk4-launch "{app_name}"
	"""
	gio.Subprocess(['sh', '-c', swaywrap_script], gio.SubprocessFlags.NONE)

class AppEntry(gtk.Widget):
	# apps will open in separate desktops
	# swaymsg "workspace '$spp_name'"
	# swaymsg "[workspace=__focused__ tiling] focus" || {
	# 	swaymsg "[workspace=__focused__] kill"
	# 	$app_command
	# }
	
	# https://docs.gtk.org/gio/method.AppLaunchContext.get_startup_notify_id.html
	# https://wayland.app/protocols/xdg-activation-v1
	
	# right click (hold) on app entries -> show close button on open app icons, plus a close all button
	# backspace or delete -> close selected app's appspace
	
	# apps will be launched by pressing "space" (or whatever mod+space corresponds to)
	
	# app = giox.DesktopAppInfo.new(desktop_file_name)
	# launch(app_name)

class AppsList:
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
			if app_name = "settings":
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

def create_password_entry() -> gtk.Entry:
	# if correct password is entered (su nu -c true): close password layer, swaymsg workspace lock
	# the password layer has a 60 sec (10 sec on battery) idle timer that will turn the screens off:
	# 	swaymsg "output - power off; seat - idle_inhibit keyboard pointer touchpad tablet_pad tablet_tool switch;"
	# 	anchor the panel's layer to all the edges of the screen, unset title of dimmer window (this prevents hiding layers)
	# 	keyboard focus on panel window
	# upon any input activity, or if unfocused, or resume from suspend:
	# 	swaymsg "output - power on; seat - idle_inhibit keyboard pointer touchpad tablet_pad touch tablet_tool switch"
	# 	unanchor the panel's layer from top left and right edges, reset title of dimmer window to "dim-layer"
	# 	keyboard focus on passwrod entry
	
	# when password is entered correctly, set panel's layer to BOTTOM, show apps view
	
	# double tap -> turn on the screen
	# gio.Subprocess(["swaymsg", "output - power on"], gio.SubprocessFlags.NONE)
	
	# on touch screen:
	# , if an unlock pattern is set, show pattern unlocking
	# , otherwise ask for password, and if no keyboard is connected, show virtual keyboard,
	# 	and after the password is entered correctly, ask user to set a pattern

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
	
	# when panel's window is focused:
	# if in locked mode, anchor panel to all edges, and show password entry
	# otherwise go to apps
	
	# FlowBox containing apps
	# https://github.com/otsaloma/catapult
	# https://github.com/abenz1267/walker
	scrolled_window = gtk.ScrolledWindow()
	scrolled_window.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.AUTOMATIC)
	window.set_child(scrolled_window)
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
	
	# app entries
	# flowbox.append(app_entry)
	
	# three buttons at top
	# left: super prompt (selected by default)
	# center: terminal views (press ';,.)
	# right: system menu (press enter)
	
	# from gi.repository import Vte as vte
	# vte.Terminal()
	
	# an item for screenshot and screencast
	# put in clipboard
	# grim -o "$$HOME/.cache/screen.png" | wl-copy --type text/uri-list "file://$$HOME/.cache/screen.png"
	
	# press escape: close panel
	
	# when window is focused, return back to apps list
	
	# implement an interface to select and close applications (keyboard and long'press gesture)
	
	launch('uni.Uni')
	# monitor dbus connection at uni.Uni, and when it's closed, relaunch Uni
	
	def lock():
		# show password entry
		launch('uni.UniLock')
		for window in ushell.get_windows():
			if gls.is_layer_window(window):
				gls.set_layer(window, gls.Layer.OVERLAY)
	
	# start in locked mode
	lock()
	
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Lock", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE,
		lambda: on_alttab_press(bar_window, lock)
	)
