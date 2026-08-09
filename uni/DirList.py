# https://github.com/kra-mo/hyperplane
# https://github.com/tchx84/Portfolio

# if a directory is given: show its content
# if a list of strings is given: show list view with them as root
# 	for directories show their content under them
# 	for devices, when they are selected, mount them and show their content underneath

# in the left panel show the storage devices, and the projects group directories inside them
# list of storage devices is obtained using "usm"

# ask the user if she wants to format the device, if:
# , it's not formatted
# , it's a removable storage device whose format is not vfat/exfat/btrfs
# , it's an internal storage device whose format is not btrfs

# device actions: mount, unmount, format
# use "usm" program to mount the device (if it's not mounted)
# removable storages should have a little light on them, showing if they are in use or not

# projects on VFAT/exFAT formated devices, or remote devices, will be opened as read'only
# when you try to edit them, you will be asked to copy them into a local device

# DirList
# new(rootDirs: [String])
# moveUp
# moveDown
# gotoFile
# findFile

# lock mode:
# read'only access to public projects
# only removable unencrypted storage devices will be writable

# new file in empty directory:
# , text
# , draw
# , picture from scanner
# 	https://wiki.archlinux.org/title/SANE
# 	https://github.com/alexpevzner/sane-airscan
# , picture from camera
# , video from camera
# , audio from mic
# the last four are also available for inserting into text

# archives
# use bsdtar command to decopress

# watch the git links in upm files, for new releases, and show it with a tag near the file's icon
# https://stackoverflow.com/questions/1064499/how-to-list-all-git-tags
# https://release-monitoring.org/

# downloders
# https://libtorrent.org/
# https://gitlab.gnome.org/World/Fragments
