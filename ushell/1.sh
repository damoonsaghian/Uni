#!/usr/bin/env sh

script_dir="$(dirname "$(readlink -f "$0")")"

umask 022

export TZ="$HOME/.config/tz"
export PATH="/usr/local/bin:/usr/bin:/$HOME/.local/bin"
export SHELL="bash-sec"

export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
rm -rf "$XDG_RUNTIME_DIR"
mkdir -pm 0700 "$XDG_RUNTIME_DIR"

dinit --services-dir /var/lib/dinit/user --services-dir /usr/share/dinit/user

start_cli() {
	# ask:
	# , auto repair (if no internet and no LAN, setup network; upm update; restart tty1)
	# , backup
	# , copy projects
	# , terminal: ask user for lockscreen password, and exit if wrong
	# , exit
	# , poweroff
	
	exec bash-sec -l
}

if [ "$(tty)" = "/dev/tty1" ] && [ "$(id -u)" != 0 ]; then
	python "$script_dir/2.py" || start_cli
else
	start_cli
fi
