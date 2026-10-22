#!/usr/bin/env sh

# if not called as login shell, just run bash, and ignore the rest
# if we are in Sway, run bash inside a bwrap sandbox that blocks sway's socket,
# 	and protects wayland socket using wayland security context
# this prevents a malicious program from stealing root password, by faking password entry
# https://niri-wm.github.io/niri/Security-Model.html
# so using sudo in Ushell does not suffer from these flaws:
# https://www.reddit.com/r/linuxquestions/comments/8mlil7/whats_the_point_of_the_sudo_password_prompt_if/
# https://security.stackexchange.com/questions/119410/why-should-one-use-sudo
[ "$0" = "-/usr/local/bin/ushell" ] || {
	if [ -n "$SWAYSOCK" ] && [ -n "$WAYLAND_DISPLAY" ]; then
		exec bwrap --bind / / --bind /dev/null "$SWAYSOCK" \
			--bind "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"-sandbox "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
			--bind /dev/null /usr/bin/lisgd \
			--bind /dev/null "$HOME/.config/ushell/screens" \
			--bind /dev/null "$HOME/.config/ushell/autostart" \
			-- /usr/bin/bash --rcfile /usr/share/bash/bashrc
	else
		exec /usr/bin/bash --rcfile /usr/share/bash/bashrc
	fi
}

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
	
	echo 'there was a problem in starting the graphical shell'
	
	while true; do
		echo 'rescue options:'
		# auto repair (if no internet and no LAN, setup network; upm update; restart tty1)
		# backup
		# copy projects
		echo "\n	${bs}t${be}erminal\n	${bs}e${be}xit\n	${bs}p${be}oweroff"
		printf 'choose one by typing its name: '
		read ans
		case "$ans" in
		t*) exec su -l nu ;;
		e*) exit ;;
		p*) poweroff ;;
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
	
	sway_config="$(mktemp)"
	echo -n "output * bg #222222 solid_color
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
	exec 'python3 \"$script_dir\"/1.py; swaymsg exit'
	" > "$sway_config"
	sway -c "$sway_config" || start_cli
else
	start_cli
fi
