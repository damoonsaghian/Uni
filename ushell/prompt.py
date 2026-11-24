from gi.repository import Gtk as gtk
from gi.repository import Adw as adw

def prompt_view() -> gtk.Widget:
	main_box = gtk.Box()
	
	return adw.Clamp(
		child=main_box,
		orientation=gtk.Orientation.HORIZONTAL,
		maximum_size=960,
		unit=adw.LengthUnit.SP
	)

# up/down navigate between results
# enter to run them again
# ctrl+c to copy them

# after running the command, the result will be copied to the clipboard

# screenshot and screencast
# grim -o "$$HOME/.cache/screen.png" | wl-copy --type text/uri-list "file://$$HOME/.cache/screen.png"

# https://github.com/heidefinnischen/cuneo
# https://qalculate.github.io/
# libqalculate-progs

# exchange rates and currency data
# https://frankfurter.dev/

# https://python-weather.readthedocs.io/en/latest/
# https://gnome.pages.gitlab.gnome.org/libgweather/
