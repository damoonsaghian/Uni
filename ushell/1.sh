#!/usr/bin/env sh

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
	echo 'there was a problem in starting the graphical shell'
	while true; do
		echo 'rescue options:'
		# auto repair (if no internet and no LAN, setup network; upm update; restart tty1)
		# backup
		# copy projects
		echo '\n	term: terminal (root)\n	exit'
		printf 'choose one by typing its name: '
		read ans
		case "$ans" in
		term) exec su -l ;;
		exit) exit ;;
		poweroff) poweroff ;;
		esac
	done
}

if [ "$(tty)" = "/dev/tty1" ] && [ "$(id -u)" != 0 ]; then
	ln -s "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" "$XDG_RUNTIME_DIR/${WAYLAND_DISPLAY}-sandbox"
	# todo: create an unprivilaged wayland socket in "$XDG_RUNTIME_DIR/${WAYLAND_DISPLAY}-sandbox"
	# python ffi
	# https://git.sr.ht/~emersion/wlsecctx/tree/master/item/main.c
	# https://github.com/bencejuhaasz/bcont/blob/main/src/wayland.rs
	# https://kttnr.net/blog/sandboxing-wayland-applications/
	# 	https://git.sr.ht/~whynothugo/way-secure/tree/main/item/src/main.rs
	# https://gitea.angry.im/PeterCxy/wl-mitm
	# https://github.com/mahkoh/wl-proxy/blob/master/update-protocols/src/main.rs
	# https://git.sr.ht/~gk/python-wayland
	# 	https://python-wayland.org/wayland/wp_security_context_manager_v1/
	
	SHELL=swayrun USHELL_DIR="$script_dir" sway -c "$script_dir"/sway.conf || start_cli
else
	start_cli
fi
