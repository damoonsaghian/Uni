from collections.abc import Callable
from typing import Any

from gi.repository import Gio as gio

class Menu(gtk.ListView):
	def __init__(self, items :list[MenuItem]):
		self.apps_list :List[SwayApp] = []
		
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
	
	def _list_apps(self):
    key = lambda x: x.get_filename().lower()
    for app in sorted(Gio.AppInfo.get_all(), key=key):
    	if not self.conf.ignore_only_show_in and not app.should_show(): continue
    	if not app.get_commandline(): continue
    	id = app.get_id()
    	if id == "io.otsaloma.catapult.desktop": continue
    	yield id, app
    
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
