#!/usr/bin/env sh

script_dir="$(dirname "$(readlink -f "$0")")"

umask 022

export TZ="$HOME/.config/tz"
export PATH="/usr/local/bin:/usr/bin"
export SHELL="/usr/bin/bash --rcfile /usr/share/bash/bashrc"

export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
rm -rf "$XDG_RUNTIME_DIR"
mkdir -pm 0700 "$XDG_RUNTIME_DIR"

dinit --services-dir /var/lib/dinit/user --services-dir /usr/share/dinit/user

start_cli() {
	echo 'there was a problem in starting the graphical shell'
	while true; do
		echo 'rescue options:'
		# auto repair (if no internet and no LAN, setup network; upm update; restart tty1)
		# backup
		# copy projects
		echo '\n	term: terminal\n	exit'
		printf 'choose one by typing its name: '
		read ans
		case "$ans" in
		term) su -c true "$USER" || exec /usr/bin/bash --rcfile /usr/share/bash/profile ;;
		exit) exit ;;
		poweroff) poweroff ;;
		esac
	done
}

if [ "$(tty)" = "/dev/tty1" ] && [ "$(id -u)" != 0 ]; then
	PATH="$PATH:/$HOME/.local/bin" USHELL_DIR="$script_dir" sway -c "$script_dir"/sway.conf || start_cli
else
	start_cli
fi
