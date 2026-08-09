#!/usr/bin/env python3

# wrapper around apk and cbuild

# notifications: error, update process, update finished

# high'performance linker
# https://pkgs.chimera-linux.org/package/current/main/x86_64/mold

match args[1]:
	case "install": exec(["apk", "add", args[2]])
	case "remove": exec(["apk", "del", args[2]])
	case "update":
		exec(["apk", "update"])
		
		# if interactive, and fwupd has updates available, ask user whether to update firmware
		# boot'firmware updates need special care
		# unless there is a read'only backup, firmware update is not a good idea
		# so warn and ask the user if she wants the update
		# doas fwupdmgr get-devices
		# doas fwupdmgr refresh
		# doas fwupdmgr get-updates
		# doas fwupdmgr update
	case "find": exec(["apk", "search", args[2]])

# search for ".upm" (case insensitive) in "$project_dir"
# the first one found, plus those sibling directories containing a .upm, are the packages to be built

# whenever systemd-boot or linux is updated, run bootup.sh

gitag_clone():
	# https://www.programming-books.io/essential/git/
	# https://man.archlinux.org/listing/git
	# https://git-scm.com/docs/partial-clone
	# --depth 1
	
	# to verify git tag signatures use ssh-keygen
	# git config --global gpg.format ssh
	# echo "$(git config --get user.email) namespaces=\"git\" $(cat "$path_to_ssh_public_key")
	# " >> "$path_to_allowed_signers_file"
	# git config --global gpg.ssh.allowedSignersFile "$path_to_allowed_signers_file"
	# 	https://blog.dbrgn.ch/2021/11/16/git-ssh-signatures/
	# 	https://www.git-tower.com/blog/setting-up-ssh-for-commit-signing/
	# 	https://calebhearth.com/sign-git-with-ssh
	# 	https://github.com/git/git/blob/master/Documentation/config/gpg.adoc
	# 	https://git-scm.com/docs/git-verify-tag
	# if a gpg key is given, download and build gpg package

# publish:
# keep two versions in repo
#
# a package is made of the content of a directory containg a 0.upm file
# or a <pkg-name>.upm file and all its sibling files and directories named <pkg-name> or <pkg-name>.*
#
# upm will search for upm files in the project directory and the first level of sub'directories
#
# <pkg-name>-<version>
#
# cross'built the package for all architectures mentioned in "$state_dir/upm.conf" (value of "arch" entry),
# and put the results in in "~/./upm/builds/<arch>/"
# in ".upm" scripts we can use "$carch" variable when cross'building
# "$carch" is an empty string when not cross'building

# reproducible builds
# during building, a .bdep file will be created that contains all the build dependencies and their versions,
# 	in the order mentioned in the .upm file
# this file can be used to reproduce the build
# the built files then will be compared (using the CHK of files in gnunet),
# 	and if there is any incompatabilities, the user will be notified
# use gnunet-directory to get CHK of the files in official gnunet namespace
# use gnunet-publish --simulate-only to obtain the CHK of built files
# https://stagex.tools/
