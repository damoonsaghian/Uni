#!/usr/bin/env sh

# if not called as login shell, just run bash, and ignore the rest
[ "$0" = "-/usr/local/bin/ushell" ] ||
	exec /usr/bin/bash --rcfile /usr/share/bash/bashrc

script_dir="$(dirname "$(readlink -f "$0")")"

umask 022

export TZ="$HOME/.config/tz"
export PATH="/usr/local/bin:/usr/bin:/$HOME/.local/bin"
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
rm -rf "$XDG_RUNTIME_DIR"
mkdir -pm 0700 "$XDG_RUNTIME_DIR"

dinit --services-dir /var/lib/dinit/user --services-dir /usr/share/dinit/user

start_cli() {
	local bs="\033[1m" # bold start
	local be="\033[0m" # bold end
	
	[ "$(tty)" = "/dev/tty1" ] && echo 'there was a problem in starting the graphical shell'
	
	while true; do
		echo 'rescue options:'
		# auto repair (if no internet and no LAN, setup network; upm update; restart tty1)
		# backup
		# copy projects
		echo "\n	${bs}t${be}erminal\n	${bs}e${be}xit\n	${bs}p${be}oweroff"
		printf 'choose one by typing its name: '
		read ans
		case "$ans" in
		t*) exec su nu ;;
		e*) exit ;;
		p*) poweroff ;;
		esac
	done
}

if [ "$(tty)" = "/dev/tty1" ] && [ "$(id -u)" != 0 ]; then
	sway_config="$(mktemp)"
	cat <<-EOF > "$sway_config"
	default_border none
	default_floating_border none
	output * bg #222222 solid_color
	input type:touchpad {
		tap enabled
		scroll_method two_finger
		natural_scroll enabled
	}
	focus_follows_mouse no
	seat * hide_cursor 8000
	bindsym Alt+Tab exec 'dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.AltTabPress'
	bindsym --release Alt+Tab exec 'dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.AltTabRelease'
	bindsym Alt+Escape kill
	bindsym Super+l exec 'dbus-send --dest=ushell.Ushell /ushell/Ushell ushell.Ushell.Lock'
	exec 'python3 \"$script_dir\"/1.py; swaymsg exit'
	EOF
	sway -c "$sway_config" || start_cli
else
	start_cli
fi
