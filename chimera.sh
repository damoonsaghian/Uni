# creates a Chimera Linux based system, with Ushell and Uni as the user interface

echo; echo "available storage devices:"
lsblk --nodep -o NAME,SIZE,MODEL | while read -r line; do printf "\t$line\n"; done
printf "enter the name of the target device for installation: "
read -r target_device
[ -e /sys/block/"$target_device" ] || {
	echo "there is no storage device named \"$target_device\""
	exit 1
}
printf "WARNING! all the data on \"/dev/$target_device\" will be erased; continue? (y/N) "
read -r answer
[ "$answer" = y ] || exit

sfdisk --quiet --wipe always --label gpt "/dev/$target_device" <<-EOF
size=260M, type=uefi
,
EOF
target_partitions="$(echo /sys/block/"$target_device"/"$target_device"* | sed -n "s/\/sys\/block\/$target_device\///pg")"
target_partition1="$(echo "$target_partitions" | cut -d " " -f1)"
target_partition2="$(echo "$target_partitions" | cut -d " " -f2)"

mkfs.vfat -F 32 /dev/"$target_partition1"
mkfs.btrfs -f /dev/"$target_partition2"

mount /dev/"$target_partition2" /mnt
mkdir /mnt/boot
mount /dev/"$target_partition1" /mnt/boot
mkdir /mnt/etc
genfstab -U /mnt > /mnt/etc/fstab

case "$(uname -m)" in
x86*)
	cpu_vendor_id="$(cat /proc/cpuinfo | grep vendor_id | head -n1 | sed -n "s/vendor_id[[:space:]]*:[[:space:]]*//p")"
	[ "$cpu_vendor_id" = AuthenticAMD ] && ucode=ucode-amd
	[ "$cpu_vendor_id" = GenuineIntel ] && ucode=ucode-intel
;;
esac

# linux-stable initramfs-tools tpm2-tools cryptsetup
# base-full-firmware (firmware-linux for all) fwupd base-full-core
# nyagetty util-linux-dmesg bash-completion
# util-linux-fdisk util-linux-fstrim util-linux-mkfs btrfs-progs dosfstools exfatprogs
# elogind sway
# chrony less nano opendoas syslog-ng util-linux-zramctl
# pipewire bluez networkmanager modemmanager iputils dnsmasq geoclue iio-sensor-proxy-meta
# fonts-noto fonts-noto-emoji-ttf fonts-noto-sans-cjk
# gtk4 libadwaita gtksourceview gst-plugins-good gst-plugins-rs gst-libav poppler-glib-libs webkitgtk4
# vte-gtk4 gtk4-layer-shell python-gobject
# libtorrent-rasterbar-python
# power-profiles-daemon-meta

mkdir -p /mnt/boot/loader/entries
cat <<-EOF > /mnt/boot/loader/loader.conf
default  arch.conf
timeout  0
auto-entries no
editor   no
EOF
root_uuid="$(blkid /dev/"$target_partition2" | sed -nr 's/^.*[[:space:]]+UUID="([^"]*)".*$/\1/p')"
cat <<-EOF > /mnt/boot/loader/entries/arch.conf
title   Arch Linux
linux   /vmlinuz-linux
initrd  /$ucode.img
initrd  /initramfs-linux.img
options root=UUID=$root_uuid rw
EOF
cat <<-EOF > /mnt/boot/loader/entries/arch-fallback.conf
title   Arch Linux (fallback initramfs)
linux   /vmlinuz-linux
initrd  /$ucode.img
initrd  /initramfs-linux-fallback.img
options root=UUID=$root_uuid rw
EOF

arch-chroot /mnt bootctl install
mkdir -p /mnt/etc/pacman.d/hooks
cat <<-EOF > /mnt/etc/pacman.d/hooks/95-systemd-boot.hook
[Trigger]
Type = Package
Operation = Upgrade
Target = systemd
[Action]
Description = Gracefully upgrading systemd-boot...
When = PostTransaction
Exec = /usr/bin/systemctl restart systemd-boot-update.service
EOF

# enablee networkmanager and bluez dinit service

# upm wrapper around apk
cat <<-'EOF' > /mnt/usr/local/bin/upm
#!/usr/bin/env sh
# wrapper around pacman
case $1 in
install) pacman -S $2 ;;
remove) pacman -Rs $2 ;;
update)
	pacman -Syu
	orphan_pkgs="$(pacman -Qdttq)"
	pacman -Rns $orphan_pkgs
	pacman -Sc
	;;
find) pacman -Ss $2 ;;
esac
EOF
chmod +x /mnt/usr/local/bin/upm
echo 'permit nopass nu cmd /usr/local/bin/upm' > /mnt/etc/doas.d/upm.conf
echo '* * * * * ID=autoupdate FREQ=1d/5m autoupdate' > "$new_root"/etc/cron.d/autoupdate

echo; echo "set root password"
while ! arch-chroot /mnt passwd; do
	echo "please retry"
done

# create normal user
# libseat only works for wlroots based wayland compositors
# pipewire does not use libseat; so the user must be in video and audio groups
# it's ok, since the system is single user, and only input devices must be protected (to protect root password)
# https://wiki.alpinelinux.org/wiki/Setting_up_a_new_user#Groups_for_desktop_usage
chimera-chroot /mnt useradd --base-dir / --create-home --shell /usr/local/bin/ushell nu
echo; echo "set lock'screen password"
while ! chroot /mnt passwd nu; do
	echo "please retry"
done
echo 'permit nopass nu cmd /usr/bin/passwd nu' > /mnt/etc/doas.d/passwd.conf

cat <<-'EOF' > /mnt/usr/local/bin/autologin
# set resource limits for realtime applications like the rt module in pipewire
ulimit -r 95 -e -19 -l 4194304

modprobe zram
zramctl /dev/zram0 --algorithm zstd --size "$(($(grep -Po "MemTotal:\s*\K\d+" /proc/meminfo)/2))KiB"
mkswap -U clear /dev/zram0
swapon --discard --priority 100 /dev/zram0

exec login -f nu
EOF
chmod +x /mnt/usr/local/bin/autologin

# create autologin dinit services for tty1 and tty2
# /usr/bin/agetty --skip-login --nonewline --noissue --noreset --noclear -l /usr/local/bin/autologin - ${TERM}

script_dir="$(dirname "$(readlink -f "$0")")"

# "$script_dir"/sway.conf
cp "$script_dir"/ushell.py /mnt/usr/local/bin/ushell
chmod +x /mnt/usr/local/bin/ushell

cp -r "$script_dir"/../ushell "$new_root"/usr/local/share/ushell
chmod +x "$new_root"/usr/local/share/ushell/1.sh
ln -s "$new_root"/usr/local/share/ushell/1.sh "$new_root"/usr/local/bin/ushell

cp "$script_dir"/../ushell/tz-guess.sh /mnt/etc/NetworkManager/dispatcher.d/09-tz-guess
chmod 755 /mnt/etc/NetworkManager/dispatcher.d/09-tz-guess

cp -r "$script_dir"/../uni "$new_root"/usr/local/share/
ln -s /usr/local/share/uni/1.py /mnt/usr/local/bin/uni
chmod +x /usr/local/share/uni/1.py

mkdir -p "$new_root"/usr/local/share/applications
echo '[Desktop Entry]
Name=Uni
Comment=Collaborative Development
Icon=uni
exec=qml6 /usr/local/share/uni/main.qml
StartupNotify=true
Type=Application
' > "$new_root"/usr/local/share/applications/uni.desktop
mkdir -p "$new_root"/usr/local/share/icons/hicolor/scalable/apps
ln -s /usr/local/share/uni/data/uni.svg "$new_root"/usr/local/share/icons/hicolor/scalable/apps/

chmod +x "$new_root"/usr/local/share/uni/usm.sh
ln -s /usr/local/share/uni/usm.sh "$new_root"/usr/local/bin/usm
echo 'permit nopass nu cmd /usr/local/bin/sd' > "$new_root"/etc/doas.d/sd.conf

echo; echo "installation completed successfully"
printf "reboot the system? (Y/n) "
read -r ans
[ "$ans" != n ] && [ "$ans" != no ] && reboot
