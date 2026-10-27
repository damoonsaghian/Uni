# for GTK4 Layer Shell to get linked before libwayland-client, we must explicitly load it before importing with gi
import ctypes
ctypes.CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk

from bar import setup_bar
from displays import setup_displays
from floater import setup_floater
from idle_manager import setup_idle_manager
from osk import setup_osk
from panel import setup_panel
from voicekey import setup_voicekey

def on_startup(ushell :gtk.Application):
	setup_bar(ushell)
	setup_displays(ushell)
	setup_floater(ushell)
	setup_idle_manager(ushell)
	setup_osk(ushell)
	setup_panel(ushell)
	setup_voicekey(ushell)

gtk.Settings.get_default().props.gtk_overlay_scrolling = False

css_provider = gtk.CssProvider(prefers_color_scheme=gtk.InterfaceColorScheme.DARK)
css_provider.load_from_resource('/org/gnome/Adwaita/styles/gtk.css')
gtk.StyleContext.add_provider_for_display(
	gdk.Display.get_default(),
	css_provider,
	gtk.STYLE_PROVIDER_PRIORITY_THEME
)

ushell = gtk.Application(application_id='ushell.Ushell')
ushell.connect('startup', on_startup)
ushell.run()
