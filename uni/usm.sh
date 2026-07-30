#!/usr/bin/env sh

# unified storage manager
# mounting and formatting storage devices
# if run as normal user, use dbus API of udisks, and if not available, notify the user
# 	https://storaged.org/udisks/docs/ref-dbus.html
# otherwise implement it using posix commands

usage_error() {
	echo "usage:"
	echo "	sd mount <dev-name>"
	echo "	sd unmount <dev-name>"
	echo "	sd mkbtrfs <dev-name>"
	echo "	sd mkfat <dev-name>"
	echo "	sd mkexfat <dev-name>"
	exit 1
}

device_name="$(basename "$2")"
[ -n "$device_name" ] && usage_error


[ "$1" = mount ] && {
	[ -e /sys/block/"$device_name" ] || {
		echo "there is no storage device named \"$device_name\""
		exit 1
	}
	
	fstype="$(blkid /dev/"$device_name" | sed -rn 's/.*TYPE="(.*)".*/\1/p')"
	if [ "$fstype" = vfat ]; then
		# it seems that vfat does not mount with discard as default (unlike btrfs)
		# if queued trim is supported, use discard option when mounting
		discard_opt=
		if [ "$(cat /sys/block/"$device_name"/queue/discard_granularity)" -gt 0 ] &&
			[ "$(cat /sys/block/"$device_name"/queue/discard_max_bytes)" -gt 2147483648 ]
		then
			discard_opt="discard,"
		fi
		
		if [ -n "$SUDO_UID" ] && [ -n "$SUDO_GID" ]; then
			mount -o ${discard_opt}nosuid,nodev,uid="$SUDO_UID",gid="$SUDO_GID" "$2" /nu/.local/state/mounts/"$device_name"
		else
			mount -o ${discard_opt}nosuid,nodev "$2" /nu/.local/state/mounts/"$device_name"
		fi
	else
		mount -o nosuid,nodev "$2" /nu/.local/state/mounts/"$device_name"
	fi
	exit
}

[ "$1" = unmount ] && {
	mount_point=/nu/.local/state/mounts/"$device_name"
	[ -d "$mount_point" ] || {
		echo "there is no mounted storage device named \"$device_name\""
		exit 1
	}
	
	# run fstrim for devices supporting unqueued trim
	[ "$(cat /sys/block/"$device_name"/queue/discard_granularity)" -gt 0 ] &&
	[ "$(cat /sys/block/"$device_name"/queue/discard_max_bytes)" -lt 2147483648 ] &&
		fstrim "$mount_point"
	
	umount "$mount_point"
	exit
}

[ "$1" != mkbtrfs ] && [ "$1" != mkfat ] && [ "$1" != mkexfat ] && usage_error

[ -e /sys/block/"$device_name" ] || {
	echo "there is no storage device named \"$device_name\""
	exit 1
}

# if $device_name is a partition, set it to the parent device
device_num="$(cat /sys/class/block/"$device_name"/dev | cut -d ":" -f 1):0"
device_name="$(basename "$(readlink /dev/block/"$device_num")")"

# exit if $device_name is the root device
root_partition="$(mount -l | grep " on / " | cut -d ' ' -f 1 | sed -n "s@/dev/@@p")"
root_device_num="$(cat /sys/class/block/"$root_partition"/dev | cut -d ":" -f 1):0"
root_device="$(basename "$(readlink /dev/block/"$root_device_num")")"
if [ "$device_name" = "$root_device" ]; then
	echo "can't install on \"$device_name\"; it contains the running system"
	exit 1
fi

case "$1" in
mkbtrfs)
	mkfs.btrfs -f /dev/"$device_name"
	mount_dir="$(mktemp -d)"
	trap "trap - EXIT; umount '$mount_dir'; rmdir '$mount_dir'" EXIT INT TERM QUIT HUP PIPE
	mount /dev/"$device_name" "$mount_dir"
	chmod 777 "$mount_dir"
	;;
mkfat) mkfs.vfat -I -F 32 /dev/"$device_name" ;;
mkexfat) mkfs.exfat /dev/"$device_name" ;;
esac
