import pathlib

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

from prompt import prompt_view
from system import system_view

script_dir = pathlib.Path(__file__).resolve().parent

#!/usr/bin/env sh

# run programs in a bwrap sandbox that blocks sway's socket,
# 	and protects wayland socket using wayland security context
# this prevents a malicious program from stealing root password, by faking password entry
# https://niri-wm.github.io/niri/Security-Model.html
# so using sudo in Ushell does not suffer from these flaws:
# https://www.reddit.com/r/linuxquestions/comments/8mlil7/whats_the_point_of_the_sudo_password_prompt_if/
# https://security.stackexchange.com/questions/119410/why-should-one-use-sudo
#
# program="$@"
# [ -z "$program" ] && program="/usr/bin/bash --rcfile /usr/share/bash/bashrc"
#
# bwrap --bind / / --bind /dev/null "$SWAYSOCK" \
# 	--bind "$XDG_RUNTIME_DIR/${WAYLAND_DISPLAY}-sandbox" "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
# 	--bind /dev/null "$HOME/.config/ushell/screens" \
# 	--bind /dev/null "$HOME/.config/ushell/autostart" \
# 	-- $program

def setup_panel(app :gtk.Application):
	window = gtk.Window(application=app)
	window.set_default_size(width=294, height=360)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.BACKGROUND)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_margin(window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(window, gls.KeyboardMode.EXCLUSIVE)
	window.present()
	
	# when a "Launcher" message is received from dbus, 
	def launcher_or_unlocker():
		# if in lock workspace, show password prompt
		# otherwise, show the launcher: gls.set_layer(window, gls.Layer.TOP)
	app.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "Launcher", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, launcher_or_unlocker)
	
	# swaymsg:
	# bindsym --release Super_L exec "dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Launcher"
	# bindsym --release Super_R exec "dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Launcher"
	# bindsym Mod1+Tab exec "dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Launcher"
	
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
	
	# an item for screenshot and screencast
	# put in clipboard
	# grim -o "$$HOME/.cache/screen.png" | wl-copy --type text/uri-list "file://$$HOME/.cache/screen.png"
	
	# press escape or click/tap outside of launcher: close launcher
	# don't close launcher, if workspace is empty
	
	# close window when unfocused

	# when "Launcher" message is recsived from dbus, present window
	
	# when window is focused, return back to apps list
	
	gio.Subprocess(['swaymsg', 'assign [app_id="uni.Uni"] workspace uni.Uni'], gio.SubprocessFlags.NONE)
	app_exec = 
	gio.Subprocess(['sh', '-c', f'{script_dir}/swaywrap.sh', app_exec], gio.SubprocessFlags.NONE)
	# monitor dbus connection at uni.Uni, and when it's closed relaunch Uni

class AppEntry(gtk.Widget):
	pass
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
	
	# gio.Subprocess(['sh', '-c', f'{script_dir}/swaywrap.sh', app_exec], gio.SubprocessFlags.NONE)

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
