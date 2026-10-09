import datetime

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def setup_bar(ushell :gtk.Application):
	notifications_box = gtk.Box(spacing=5)
	setup_notifications(notification_box)
	system_status_box = gtk.Box(spacing=5)
	setup_system_status(system_status_box)
	
	window = gtk.Window(application=ushell)
	window.set_default_size(width=-1, height=18)
	window.set_child(gtk.CenterBox(
		start_widget=notification_box,
		end_widget=system_status_box,
		margin_start=2,
		margin_end=2
	))
	
	setup_click_evctl(window)
	
	# when there is a fullscreen window, there is no bar to click on
	# so a hot edge will be created that will reveal the bar when pointer touches the bottom edge
	setup_hot_edge(ushell, window)
	
	setup_touchscreen_gesture(window)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.BOTTOM)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_anchor(window, gls.Edge.LEFT, True)
	gls.set_anchor(window, gls.Edge.RIGHT, True)
	gls.auto_exclusive_zone_enable(window)
	gls.set_keyboard_mode(window, gls.KeyboardMode.NONE)
	
	window.present()

def setup_click_evctl(window :gtk.Window):
	# click to toggle the main panel
	def on_click():
		gio.Subprocess(["dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Panel"], gio.SubprocessFlags.NONE)
	click_evctl = gtk.GestureClick(button=1, exclusive=True) # exclusive: only pointer events
	click_evctl.connect('begin', on_click)
	window.add_controller(click_evctl)
	
	# right click or long'press to show app closer dialog popup (at click position)
	def popup_close_dialog():
		pass
	right_click_evctl = gtk.GestureClick(button=3, exclusive=True)
	right_click_evctl.connect('begin', popup_close_dialog)
	window.add_controller(right_click_evctl)
	# long press
	longpress_evctl = gtk.GestureLongPress()
	longpress_evctl.connect('begin', popup_close_dialog)
	window.add_controller(longpress_evctl)

def setup_hot_edge(ushell :gtk.Application, bar_window :gtk.Window):
	window = gtk.Window(application=ushell)
	window.set_default_size(width=-1, height=1)
	setup_click_evctl(window)
	
	# when pointer enters it, set the layer of bar_window to overlay, so it will show above fullscreen window
	# gls.set_layer(bar_window, gls.Layer.OVERLAY)
	# when mouse leaves bar, if pointer is not on edge, set the bar layer back to bottom
	# gls.set_layer(bar_window, gls.Layer.BOTTOM)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.OVERLAY)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_anchor(window, gls.Edge.LEFT, True)
	gls.set_anchor(window, gls.Edge.RIGHT, True)
	gls.set_exclusive_zone(window, -1)
	gls.set_keyboard_mode(window, gls.KeyboardMode.NONE)
	gls.set_respect_close(window, True)
	
	window.present()

def setup_touchscreen_gesture(bar_window :gtk.Window):
	# swipe up from the bottom edge without lifting the finger, just a little, enough to reveal the bar
	# continue to complete the swipe, to open panel as well
	gio.Subprocess(['sh', "[ -e /dev/input/touchscreen ] && doas lisgd "
		"-g '1,DU,B,*,P,dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.OverlayBar'"
		"-g '1,DU,B,*,R,dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Panel'"
	], gio.SubprocessFlags.NONE)
	
	overlay_dim = gtk.Window(application=ushell)
	# the moment this window recieves a click event, it hides itself, then hide_all(ushell)
	def hide_all():
		for window in ushell.get_windows():
			if gls.is_layer_window(window):
				gls.set_layer(window, gsl.Layer.BOTTOM)
	gls.init_for_window(overlay_dim)
	gls.set_layer(overlay_dim, gls.Layer.OVERLAY)
	gls.set_anchor(overlay_dim, gls.Edge.LEFT, True)
	gls.set_anchor(overlay_dim, gls.Edge.RIGHT, True)
	gls.set_anchor(overlay_dim, gls.Edge.TOP, True)
	gls.set_anchor(overlay_dim, gls.Edge.BOTTOM, True)
	gls.set_keyboard_mode(overlay_dim, gls.KeyboardMode.NONE)
	gls.set_respect_close(overlay_dim, True)
	
	def reveal_bar():
		gls.set_layer(bar_window, gls.Layer.OVERLAY)
		
		def show_overlay_dim():
			overlay_dim.present()
		app.get_dbus_connection().signal_subscribe(
			None, "ushell.Ushell", "OverlayDim", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, show_overlay_dim)
	ushell.get_dbus_connection().signal_subscribe(
		None, "ushell.Ushell", "OverlayBar", "/ushell/Ushell", None, gio.DBusSignalFlags.NONE, reveal_bar)

def setup_notifications(box :gtk.Box):
	pass
	# temporary show the message on the bar
	# after that just show app icon and the number of notifications (if there are more than one)
	# https://specifications.freedesktop.org/notification/latest/protocol.html
	# https://github.com/halhen/statnot
	# https://github.com/mk-fg/notification-thing
	
	# alerts (important notifications like clock alerts, or public emergency warnings):
	# , the message remains
	# , it blinks
	# , display is powered on
	# , alert sound is played repeatedly until user input
	# https://invent.kde.org/webapps/foss-public-alert-server/

def setup_system_status(box :gtk.Box):
	# https://gitlab.gnome.org/GNOME/gnome-usage
	# https://pkgs.alpinelinux.org/package/edge/main/x86_64/smartmontools
	
	# screen recorder indicator
	# watch for $HOME/.cache/swaycap/screen.mp4
	# if it's open, show red circle
	# if exists but not open, show red square
	# if does not exist, shoe nothing
	
	# cam
	# visible only when it's active
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/camera.js
	
	# audio (pipewire output)
	# if audio out device is not dummy, show icon
	# 0: muted icon
	# 1 to 80: low icon
	# 80 to 99: medium icon
	# 100: high icon
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/volume.js
	
	# mic (pipewire input)
	# https://github.com/xenomachina/i3pamicstatus
	
	# bluetooth
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/bluetooth.js
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/bluetooth.py
	
	# wifi
	# if exists, show icon
	# 0 to 20: none icon
	# 20 to 50: weak icon
	# 50 to 80: ok icon
	# 80 to 90: good icon
	# 90 to 100: excellent icon
	# https://wireless.wiki.kernel.org/en/users/documentation/iw
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/wifi.py
	
	# cell
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/wwan.py
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/wwan_status.py
	
	# gnunet
	# icon's color indicates average speed (download+upload) in the last 30 seconds:
	# , 0 to 10 kB/s: white icon
	# , 10 kbs to 100 kB/s: yellow icon
	# , 100 kbs to 1 MB/s: green icon
	# , greater than 1 MB/s: blue icon
	# show upload speed, and total upload since boot, in the top index
	# show download speed, and total download since boot, in the bottom index
	# when there is upload/download make the icon green
	
	# internet
	# https://doc.qt.io/qt-6/qml-qtnetwork-networkinformation.html
	# icon's color indicates average speed (download+upload) in the last 30 seconds:
	# , 0 to 10 kB/s: white icon
	# , 10 kbs to 100 kB/s: yellow icon
	# , 100 kbs to 1 MB/s: green icon
	# , greater than 1 MB/s: blue icon
	# show upload speed, and total upload since boot, in the top index
	# show download speed, and total download since boot, in the bottom index
	# when there is upload/download make the icon green
	# online status
	# https://github.com/AstraExt/astra-monitor/tree/main/src/network
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/netdata.py
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/net_rate.py
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/network.js
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/rfkill.js
	# https://github.com/AlynxZhou/gnome-shell-extension-net-speed/blob/master/extension.js
	# https://github.com/rishuinfinity/InternetSpeedMonitor/blob/master/src/extension.js
	# https://github.com/eeeeeio/gnome-shell-extension-nano-system-monitor/blob/master/src/extension.js
	# active_net_device="$(networkctl list | grep routable | { read -r _ net_dev _; echo $net_dev; })"
	# [ -n "$active_net_device" ] && {
	# 	read -r internet_rx < "/sys/class/net/$active_net_device/statistics/rx_bytes"
	# 	read -r internet_tx < "/sys/class/net/$active_net_device/statistics/tx_bytes"
	# 	internet_total=$(( (internet_rx + internet_tx)/100000 ))
	# 	
	# 	internet_speed=$(( (internet_total - last_internet_total) / interval ))
	# 	last_internet_total=$internet_total
	# 	
	# 	# if there was network activity in the last 60 seconds, set color to green
	# 	internet_speed_average=$(( (internet_speed + internet_speed_average*lmaf) / (lmaf+1) ))
	# 	[ "$internet_speed_average" = 0 ] || internet_icon_foreground_color="foreground=\"green\""
	# 	
	# 	# each 20 seconds check for online status
	# 	internet_online=1
	# 	[ "$internet_online" = 0 ] && internet_icon_foreground_color='foreground="red"'
	# 	
	# 	internet_speed="$(( internet_speed/10 )).$(( internet_speed%10 ))"
	# 	internet_total="$(( internet_total/10000 )).$(( (internet_total/1000)%10 ))"
	# 	internet="$internet_total<span $internet_icon_foreground_color>  </span>$internet_speed"
	# }
	
	# cpu cores
	# show as gray vertical bars updated every second
	# https://github.com/AstraExt/astra-monitor/tree/main/src/processor
	# https://gitlab.gnome.org/GNOME/gnome-usage/-/blob/main/src/cpu-monitor.vala
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/sysdata.py
	# https://github.com/fcaballerop/simple-monitor-gnome-shell-extension/blob/main/extension.js
	# https://github.com/eeeeeio/gnome-shell-extension-nano-system-monitor/blob/master/src/extension.js
	
	# memory
	# white vertical bar
	# when it reaches above 90%, it blinks
	# https://github.com/AstraExt/astra-monitor/tree/main/src/memory
	# https://gitlab.gnome.org/GNOME/gnome-usage/-/blob/main/src/memory-monitor.vala
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/sysdata.py
	# https://github.com/fcaballerop/simple-monitor-gnome-shell-extension/blob/main/extension.js
	# https://github.com/eeeeeio/gnome-shell-extension-nano-system-monitor/blob/master/src/extension.js
	#
	# import re
	# with open('/proc/meminfo') as mem_info_file:
	# 	mem_info = mem_info_file.read()
	# 	mem_total = re.compile(r"MemTotal:\s+(\d+) kB").match(mem_info)
	# 	mem_total = int(mem_total)
	# 	mem_available = re.compile(r"MemAvailable:\s+(\d+) kB").match(mem_info)
	# 	mem_available = int(mem_available)
	# 	mem_usage = (mem_total - mem_available) / mem_total
	
	# storage devices activity
	# writing: red icon
	# reading: yellow icon
	# reading and writing: orange icon
	# if there is no read/write now, but there was one in the last 15 seconds, dim the corresponding color
	# https://github.com/AstraExt/astra-monitor/tree/main/src/storage
	# https://unix.stackexchange.com/questions/55212/how-can-i-monitor-disk-io
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/diskdata.py
	
	# # battery: if exist, show icon
	# https://wiki.archlinux.org/title/Laptop
	# https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/main/js/ui/status/system.js
	# https://github.com/ultrabug/py3status/blob/master/py3status/modules/battery_level.py
	# https://pkgs.chimera-linux.org/package/current/main/x86_64/upower
	# 	https://upower.freedesktop.org/docs/
	# https://www.kernel.org/doc/html/latest/power/power_supply_class.html
	# if [ -e /sys/class/power_supply/BAT0 ]; then
	# 	# /sys/class/power_supply/BAT0/capacity
	# 	# /sys/class/power_supply/BAT0/status
	# 	# https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-power
	# fi
	
	# date'time indicator
	dt = datetime.now()
	datetime_indicator = gtk.Label(dt.strftime("%Y-%m-%d %a %p %I:%M"))
	def update_datetime_indicator(_,_,_):
		dt2 = datetime.now()
		if dt2 != dt:
			dt = dt2
			datetime_indicator.set_label(dt.strftime("%Y-%m-%d %a %p %I:%M"))
	gio.File.new_for_path("/sys/class/rtc/rtc0/time").monitor_file().connect('changed',	update_datetime_indicator)
	box.append(datetime_indicator)
	# other than the system timezone, show date in universal format:
	# 	UTC timezone and Persian calendar with Deioces epoch
	# https://github.com/ilius/starcal
	# https://github.com/omid/Persian-Calendar-for-Gnome-Shell/blob/master/PersianCalendar%40oxygenws.com/PersianDate.js
	#
	# monitor "$TZ" file and modemmanager timezone
	# when one is changed check if they don't match, show the set timezone beside time
	# https://www.freedesktop.org/software/ModemManager/doc/latest/ModemManager/gdbus-org.freedesktop.ModemManager1.Modem.Time.html#gdbus-property-org-freedesktop-ModemManager1-Modem-Time.NetworkTimezone
	#
	# get current location from GeoClue
	# 	https://www.freedesktop.org/software/geoclue/docs/gdbus-org.freedesktop.GeoClue2.Location.html
	# get timezone from location
	# 	https://lazka.github.io/pgi-docs/GeocodeGlib-2.0/index.html
	# if [ -e "$HOME/.config/tz" ]; then
	# 	doas -u nu ln -s "$tzdata_path/$continent/$city" /nu/.cache/system/tz-guess
	# else
	# 	doas -u nu ln -s "$tzdata_path/$continent/$city" /nu/.config/tz
	# fi
	# waits for the location updated signal from GeoClue, then repeat

