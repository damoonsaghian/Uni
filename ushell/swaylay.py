# https://github.com/wmww/gtk4-layer-shell

# when a request is received from dbus, show the launcher

# when a request is received from dbus, create an empty window, with app_id swaydim
# it will be closed the moment it's focused

# when a request is received from dbus, create a blury fullscreen layer showing a 10 seconds countdown
# upon any input activity, close the layer
# after 10 seconds:
# , swaymsg 'mode lock; workspace lock'
# , show password layer, with a transparent window, the size of the screen
# password layer:
# , after 60 seconds of inactivity: swaymsg "output * power off"
# , and after that, when there is an input activity: swaymsg "output * power on"
# , password layer can be closed by pressing escape, or clicking outside of entry box
# , when password layer is closed, and the workspace is empty (ie "swaymsg focus" fails), run: uni lock

# https://www.freedesktop.org/wiki/Software/systemd/inhibit/

# run uni.desktop

# voice control: keybindings and typing
# https://www.speedofsound.io/
# https://github.com/kavehtehrani/speech2text-extension/
# https://github.com/k2-fsa/sherpa-onnx
# https://github.com/Saim20/willow
# https://github.com/Manish7093/IBus-Speech-To-Text
# https://github.com/canonical/myna
# https://github.com/mkiol/dsnote
# https://easyspeak.dev/latest/
# https://github.com/g0dd4rd/anthony/
