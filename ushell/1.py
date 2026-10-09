# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
import ctypes
ctypes.CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk

from bar import setup_bar
from displays import setup_displays
from floater import setup_floater
from locker import setup_locker
from osk import setup_osk
from panel import setup_panel
from voicekey import setup_voicekey

def on_startup(ushell :gtk.Application):
	setup_bar(ushell)
	setup_displays(ushell)
	setup_floater(ushell)
	setup_locker(ushell)
	setup_osk(ushell)
	setup_pannel(ushell)
	setup_voicekey(ushell)

gtk.Settings.get_default().props.gtk_overlay_scrolling = False

ushell = gtk.Application(application_id='ushell.Ushell')
ushell.connect('startup', on_startup)
ushell.run()
