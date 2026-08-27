# after 600 seconds show a 10 sec countdown layer which will be closed on any input activity
# when counter reaches 0, go to lock workspace and show the password layer
# the password layer has a 60 sec idle timer that will turn the screen off

# when the state of a window changes:
# if the focused window is tiling, kill all floating windows of current workspace
# 	then if it's not the first window of workspace, make it floating
# if workspace is empty, open the launcher

# when a floating window is open, dim the tiling window, and make it insensitive to pointer

# do not show pointer at start, and hide it after 10 sec of inactivity

# if appid and title matches a line in $HOME/.config/ushell/screens,
# create the surface in the workspace named after that screen's number

# bindsym Mod4+BackSpace kill
# bindsym Mod1+Escape kill

# keybinding to show the launcher
# release Super_L or Super_R
# Alt+tab

# when screens are added/removed:
# , take the list of workspaces (using swaymsg)
# , move the first none numeric workspace to the first output
# , move workspace 2 ... to output 2 ...
# this way, the first monitor will always remains the main monitor, even after reconnecting
# https://docs.gtk.org/gdk4/method.Display.get_monitors.html
# https://docs.gtk.org/gdk4/class.Monitor.html
# https://docs.gtk.org/gdk4/method.Monitor.get_connector.html
# https://github.com/tamirzb/qkdisplays

# https://www.freedesktop.org/wiki/Software/systemd/inhibit/

# on screen keyboard for touch screen
# https://python-wayland.org/wayland/zwp_input_method_v1/

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

# run uni.desktop
