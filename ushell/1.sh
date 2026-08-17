#!/usr/bin/env sh

script_dir="$(dirname "$(readlink -f "$0")")"

[ -f /etc/profile ] && . /etc/profile
for profile_script in /usr/share/profile/*.sh; do
	[ -f "$profile_script" ] && . "$profile_script"
done

umask 022

export TZ="$HOME/.config/tz"
export SHELL="doas -u \"$USER\" /usr/bin/bash --noprofile --norc"
export PS1='\[$(
IFS="[;" read -p $"\e[6n" -d R -rs _ _ line _
[ "$line" = 1 ] || echo
printf "%0.s─" $(seq 1 $(( COLUMNS/2 - ${#PWD}/2 - 2 )) )
)\]\e[7m \[${PWD}\] \e[0m\[$(printf "%0.s─" $(seq 1 $((COLUMNS - COLUMNS/2 + ${#PWD}/2 + 2 - ${#PWD} - 2)) ))\]\n'
export PS2=""
export PS0='\[$(printf "%0.s-" $(seq 1 $((COLUMNS)) ))\]\n'
export PATH="/usr/local/bin:/usr/bin:/$HOME/.local/bin"
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
rm -rf "$XDG_RUNTIME_DIR"
mkdir -pm 0700 "$XDG_RUNTIME_DIR"

dinit --services-dir /var/lib/dinit/user --services-dir /usr/share/dinit/user

start_cli() {
	# ask:
	# , auto repair (if no internet and no LAN, setup network; upm update; also if not on tty1, restart tty1)
	# , backup
	# , copy projects
	# , terminal: ask user for lockscreen password, and exit if wrong
	# , exit
	# , poweroff
	
	$SHELL
}

if [ "$(tty)" = "/dev/tty1" ] && [ "$(id -u)" != 0 ]; then
	sway -c "$script_dir/sway.conf" || start_cli
else
	start_cli
fi
