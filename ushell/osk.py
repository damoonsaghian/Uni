from gi.repository import GLib, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

def setup_osk(self, app: Gtk.Application):
	window = Gtk.Window(application=app)
	window.set_default_size(width=294, height=360)
	
	LayerShell.init_for_window(window)
	LayerShell.set_layer(window, LayerShell.Layer.TOP)
	LayerShell.set_anchor(window, LayerShell.Edge.BOTTOM, True)
	LayerShell.set_margin(window, LayerShell.Edge.BOTTOM, 20)
	LayerShell.set_keyboard_mode(window, LayerShell.KeyboardMode.EXCLUSIVE)

# on'screen keyboard for touch screen
# https://github.com/fortime/fcitx5-osk
# https://wiki.archlinux.org/title/Fcitx5
