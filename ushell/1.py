# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
import ctypes
ctypes.CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk as gtk

from bar import setup_bar
from dimmer import setup_dimmer
from displays import setup_displays
from locker import setup_locker
from osk import setup_osk
from panel import setup_panel
from voicekey import setup_voicekey

def on_startup(app :gtk.Application):
	setup_bar(app)
	setup_dimmer(app)
	setup_locker(app)
	setup_osk(app)
	setup_pannel(app)
	setup_screens(app)
	setup_voicekey(app)

gtk.Settings.get_default().props.gtk_overlay_scrolling = False

app = gtk.Application(application_id='ushell.Ushell')
app.connect('startup', on_startup)
app.run()
