#!/usr/bin/env sh

# run programs in a bwrap sandbox that blocks sway's socket,
# 	and protects wayland socket using wayland security context
# this prevents a malicious program from stealing root password, by faking password entry
# https://niri-wm.github.io/niri/Security-Model.html
# so running programs as root in Ushell does not suffer from these flaws:
# https://www.reddit.com/r/linuxquestions/comments/8mlil7/whats_the_point_of_the_sudo_password_prompt_if/
# https://security.stackexchange.com/questions/119410/why-should-one-use-sudo

program="$@"
[ -z "$program" ] && program="/usr/bin/bash --rcfile /usr/share/bash/bashrc"

bwrap --bind / / --bind /dev/null "$SWAYSOCK" \
	--bind "$XDG_RUNTIME_DIR/${WAYLAND_DISPLAY}-sandbox" "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" \
	-- $program
