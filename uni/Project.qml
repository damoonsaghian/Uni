// if there is a saved session file for the project, restore it

// ".cache/codev/notif-*" files: notifications

/*
for a new project create "$project_dir/.meta/gnunet" file containing these lines:
, project name
, the level of anonymity
, gnunet namespaces (public key of the egos that can publish the project)

an ego (key pair) for each project group
when creating a project group, offer the user to create a new ego, or reuse the ego of other groups

implement the user interface to add or remove egos from "$project_dir/.meta/gnunet"
*/

// https://docs.gnunet.org/latest/users/gns.html#revocation
// https://docs.gnunet.org/latest/developers/apis/revocation.html
// the revoke message will be pre'calculated (can take days or weeks)

// watch the git links in Ubuild.sh files, for new releases, and notify the user
// https://stackoverflow.com/questions/1064499/how-to-list-all-git-tags
// https://release-monitoring.org/

/*
function hash2path() {}

function path2hash() {
	// for any file in wdir, newer than the hash file (in pristine), calculate its hash,
	// copy (reflink) it to its hash'named path
	// for any entry in the hash file, if the file exists in wdir, copy it too
}

class Project {
	pull(gnNamespace) {
		// `cp --rflink=auto "${project_dir}"/* "${project_dir}"/.cache/ushare/pull/`
		// show a three'way diff, based on the main branch, pristine, and the working directory
		// then the user will be asked to accept all or some parts of the diff
	}
	
	pullRequest() {
		// first publish the pristine and the working directory (except .cache)
		// then send the two addresses to the main developer
	}
	
	pullRequestRetrieve(pristineUri, wdirUri) {
		// send a message to the main developer
		// unpublish the two links (printine and the working directory)
	}
	
	pullRequestAnswer(pristineUri, branchUri) {
		// this will be run by the main developer
		// make a diff based on the sent pristine and branch, plus our own working directory	
		
		// pull requests can be kept to trace backdoors found later, back to the origin author
	}
	
	publish(gnNamespace, projectName) {
		// for any file in wdir, newer than the hash file (in pristine), calculate its hash, copy it to its hash'named path
		// for any entry in the hash file, if the file exists in wdir, copy it too
		// gnunet publish
	}
	
	publishPackage() {
	}
}
*/

/*
class ProjectView {
	dir: String,
	widget: Overlay, // floating layer can be used to view web'pages, images and videos
	mainView: ListBox,
	files: Files,
	centerView: Stack
	
	new(dirPath) {
		self.dirPath = dirPath;
		self.widget: Overlay = new Overlay();
		let mainBox = new Box(orient: HORIZONTAL);
		widget.setChild(mainBox);
		
		self.files = new Files();
		mainBox.append(files);
		
		self.centerView = new Stack();
		mainBox.append(centerView);
	}
}
*/

import QtQuick

Item {
    id: root
}
