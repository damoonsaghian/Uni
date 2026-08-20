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

new_root=/media/root
mkdir "$new_root"
mount /dev/"$target_partition2" "$new_root"
mkdir "$new_root"/boot
mount /dev/"$target_partition1" "$new_root"/boot
mkdir "$new_root"/etc
genfstab -U "$new_root" > "$new_root"/etc/fstab

case "$(uname -m)" in
x86*)
	cpu_vendor_id="$(cat /proc/cpuinfo | grep vendor_id | head -n1 | sed -n "s/vendor_id[[:space:]]*:[[:space:]]*//p")"
	[ "$cpu_vendor_id" = AuthenticAMD ] && ucode_pkg=ucode-amd
	[ "$cpu_vendor_id" = GenuineIntel ] && ucode_pkg=ucode-intel
;;
esac

chimera-bootstrap "$new_root" systemd-boot $ucode_pkg linux-stable base-full-kernel base-full-firmware \
	base-full-core chrony nyagetty util-linux-dmesg util-linux-zramctl \
	util-linux-fdisk util-linux-fstrim util-linux-mkfs btrfs-progs dosfstools exfatprogs \
	bluez networkmanager modemmanager iputils dnsmasq geoclue iio-sensor-proxy-meta \
	base-full-session pipewire bash-completion less nano opendoas fwupd chimera-repo-user \
	sway jq gtk4-layer-shell fonts-noto fonts-noto-emoji-ttf fonts-noto-sans-cjk \
	libadwaita gtksourceview gst-plugins-good gst-plugins-rs gst-libav poppler-glib-libs webkitgtk4 vte-gtk4 \
	python-gobject libtorrent-rasterbar-python

chimera-chroot "$new_root" update-initramfs -c -k all
chimera-chroot "$new_root" bootctl install
chimera-chroot "$new_root" gen-systemd-boot

# zram swap
cat <<-'EOF' > "$new_root"/usr/local/share/zram-swap.sh
modprobe zram
zramctl /dev/zram0 --algorithm zstd --size "$(($(grep -Po "MemTotal:\s*\K\d+" /proc/meminfo)/2))KiB"
mkswap -U clear /dev/zram0
swapon --discard --priority 100 /dev/zram0
fi
EOF
echo 'type = scripted
command = /usr/bin/sh /usr/local/share/zram-swap.sh
depends-on = early-prepare.target
depends-on = early-devd
before = early-fs-pre.target
' > "$new_root"/usr/local/lib/dinit.d/zram-swap
chimera-chroot "$new_root" dinitctl enable zram-swap

chimera-chroot "$new_root" dinitctl enable networkmanager
chimera-chroot "$new_root" dinitctl enable bluetoothd

# upm wrapper around apk
cat <<-'EOF' > "$new_root"/usr/local/bin/upm
#!/usr/bin/env sh
# wrapper around pacman
case $1 in
install) apk add $2 ;;
remove) apk del $2 ;;
update)	apk update;	apk upgrade	;;
find) apk search $2 ;;
esac
EOF
chmod +x "$new_root"/usr/local/bin/upm
echo 'permit nopass nu cmd /usr/local/bin/upm' > "$new_root"/etc/doas.d/upm.conf

echo; echo "set root password"
while ! chimera-chroot "$new_root" passwd; do
	echo "please retry"
done

# create normal user
chimera-chroot "$new_root" useradd --base-dir / --create-home --shell /usr/local/bin/ushell nu
echo; echo "set lock'screen password"
while ! chroot "$new_root" passwd nu; do
	echo "please retry"
done
echo 'permit nu cmd /usr/bin/passwd nu' > "$new_root"/etc/doas.d/passwd.conf

# set autologin for tty1 and tty2
echo 'GETTY_ARGS="$GETTY_ARGS --autologin nu"' > "$new_root"/etc/default/agetty-tty1
cp "$new_root"/etc/default/agetty-tty1 "$new_root"/etc/default/agetty-tty2

echo '#!/usr/bin/env sh
# bash secured by not running bashrc and profile in home directory
if [ "$1" = "-l" ]; then
	/usr/bin/bash --rcfile /etc/profile
else
	/usr/bin/bash --rcfile /usr/share/bash/bashrc
fi
' > "$new_root"/usr/local/bin/bash-sec
chmod +x "$new_root"/usr/local/bin/bash-sec

cat <<-'EOF' > "$new_root"/etc/bash/bashrc.d/prompt.sh
PS1='\[$(
IFS="[;" read -p $"\e[6n" -d R -rs _ _ line _
[ "$line" = 1 ] || echo
printf "%0.s─" $(seq 1 $((COLUMNS/2 - ${#PWD}/2 - 1)) )
)\]\e[7m \[${PWD}\] \e[0m\[$(printf "%0.s─" $(seq 1 $((COLUMNS - COLUMNS/2 + ${#PWD}/2 + 2 - ${#PWD} - 3)) ))\]\n'
PS2=""
PS0='\[$(printf "%0.s-" $(seq 1 $((COLUMNS)) ))\]\n'
EOF

script_dir="$(dirname "$(readlink -f "$0")")"

cp -r "$script_dir"/ushell "$new_root"/usr/local/share/
chmod +x "$new_root"/usr/local/share/ushell/1.sh
ln -s /usr/local/share/ushell/1.sh "$new_root"/usr/local/bin/ushell
chmod 755 "$new_root"/usr/local/share/ushell/tz-guess.sh
ln -s /usr/local/share/ushell/tz-guess.sh "$new_root"/etc/NetworkManager/dispatcher.d/09-tz-guess

cp -r "$script_dir"/uni "$new_root"/usr/local/share/
chmod +x "$new_root"/usr/local/share/uni/1.py
ln -s /usr/local/share/uni/1.py "$new_root"/usr/local/bin/uni
chmod +x "$new_root"/usr/local/share/uni/usm.sh
ln -s /usr/local/share/uni/usm.sh "$new_root"/usr/local/bin/usm
echo 'permit nopass nu cmd /usr/local/bin/usm' > "$new_root"/etc/doas.d/usm.conf

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
cp "$script_dir"/.data/icon.svg "$new_root"/usr/local/share/icons/hicolor/scalable/apps/uni.svg

echo; echo "installation completed successfully"
printf "reboot the system? (Y/n) "
read -r ans
[ "$ans" != n ] && [ "$ans" != no ] && reboot
