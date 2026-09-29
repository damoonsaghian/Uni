from gi.repository import Gtk as gtk
from gi.repository import Gtk4LayerShell as gls

def setup_osk(app :gtk.Application):
	window = gtk.Window(application=app)
	window.set_default_size(width=294, height=360)
	
	gls.init_for_window(window)
	gls.set_layer(window, gls.Layer.TOP)
	gls.set_anchor(window, gls.Edge.BOTTOM, True)
	gls.set_margin(window, gls.Edge.BOTTOM, 20)
	gls.set_keyboard_mode(window, gls.KeyboardMode.EXCLUSIVE)

# on'screen keyboard for touch screen
# https://github.com/fortime/fcitx5-osk
# https://wiki.archlinux.org/title/Fcitx5
