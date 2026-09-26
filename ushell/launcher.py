from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell

def setup_launcher(app :Gtk.Application):
	window = Gtk.Window(application=app)
	window.set_default_size(width=294, height=360)
	
	LayerShell.init_for_window(window)
	LayerShell.set_layer(window, LayerShell.Layer.TOP)
	LayerShell.set_anchor(window, LayerShell.Edge.BOTTOM, True)
	LayerShell.set_margin(window, LayerShell.Edge.BOTTOM, 20)
	LayerShell.set_keyboard_mode(window, LayerShell.KeyboardMode.EXCLUSIVE)
	
	# when a "Launcher" message is received from dbus, 
	def launcher_or_unlocker():
		# if in lock workspace, show password prompt
		# otherwise, show the launcher: window.present()
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.SwayShell", "Launcher", "/ushell/SwayShell", None, Gio.DBusSignalFlags.NONE, launcher_or_unlocker)
	
	# FlowBox containing apps
	# https://github.com/otsaloma/catapult
	# https://github.com/abenz1267/walker
	scrolled_window = Gtk.ScrolledWindow()
	scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
	window.set_child(scrolled_window)
	flowbox = Gtk.FlowBox()
	flowbox.set_margin_top(12)
	flowbox.set_margin_end(12)
	flowbox.set_margin_bottom(12)
	flowbox.set_margin_start(12)
	flowbox.set_valign(Gtk.Align.START)
	flowbox.set_max_children_per_line(5)
	flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
	scrolled_window.set_child(flowbox)
	# flowbox.insert(widget)
	
	# app entries
	# flowbox.append(app_entry)
	
	# three buttons at top
	# left: super prompt (selected by default)
	# center: terminal views (press ';,.)
	# right: system menu (press enter)
	
	# an item for screenshot and screencast
	# put in clipboard
	# grim -o "$$HOME/.cache/screen.png" | wl-copy --type text/uri-list "file://$$HOME/.cache/screen.png"
	
	# press escape or click/tap outside of launcher: close launcher
	# don't close launcher, if workspace is empty
	
	# close window when unfocused

	# when "Launcher" message is recsived from dbus, present window

class AppEntry(Gtk.Widget):
	pass
	
	script_dir = pathlib.Path(__file__).resolve().parent
	# ["sh", str(script_dir/"swayrun.sh"), app_exec]
	# apps will open in separate desktops
	# swaymsg "workspace '$spp_name'"
	# swaymsg "[workspace=__focused__ tiling] focus" || {
	# 	swaymsg "[workspace=__focused__] kill"
	# 	$app_command
	# }
	
	# right click (hold) on app entries -> show close button on open app icons, plus a close all button
	# backspace or delete -> close selected app's appspace
	
	# apps will be launched by pressing "space" (or whatever mod+space corresponds to)

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
	# subprocess.run([
	# 	'swaymsg',
	# 	f'[app_id=codev] move workspace {app_name}; workspace {app_name}' 
	# ])
	# if not subprocess.run(['swaymsg', '[floating] focus']):
	# 	subprocess.run(['swaymsg', 'exec ' + app_item.get_executable()])

	# notify:has-focus: select system

	# app list is a flowbox whose model is a list store that will be updated when .desktop files of apps changes
	def compare_apps(self, app1 :Gio.AppInfo, app2 :Gio.AppInfo):
		app1_name = app1.get_name()
		app2_name = app2.get_name()
		if app2_name > app1_name:
			return -1
		if app1_name > app2_name:
			return 1
		return 0
	def update_apps_list(self):
		self.apps_list.remove_all()
		for app in Gio.AppInfo.get_all():
			if app.should_show():
				self.apps_list.insert_sorted(app, self.compare_apps)
		settings_app = Gio.AppInfo.create_from_commandline("settings")
		self.apps_list.insert(0, settings_app)
	def create_widget(self, app_item :Gio.AppInfo):
		app_name = app_item.get_name()
		label = Gtk.Label(
			label = app_name,
			justify = Gtk.Justification.CENTER,
			width_chars = 20
		)
		icon = app_item.get_icon()
		if not icon:
			if app_name = "settings":
				icon = Gio.ThemedIcon("applications-system-symbolic")
			else:
				icon = Gio.ThemedIcon("")
		icon_image = Gtk.Image.new_from_gicon(icon)
		widget = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 5)
		widget.append(icon_image)
		widget.append(label)
		return widget
	# the first element is selected by default
	# when an item in the flowbox is clicked, run the app
	# 	selected_child :Gtk.FlowBoxChild = apps_flowbox.get_selected_children()[0]
	# 	index = selected_child.get_index()
	# 	self.selected_item = self.apps_list.get_item(index)
	# 	self.on_activate()
