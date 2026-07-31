#!/usr/bin/env qml6

import QtQuick
import QtQuick.Controls
import org.mauikit.controls as Maui

Maui.ApplicationWindow {

// to make maximize state of window, persistent
Settings { property alias visibility: parent.visibility }

Binding { target: Application; property: "name"; value: "Uni" }
Binding { target: Application; property: "organization"; value: "Uni" }
Binding { target: Application; property: "domain"; value: "uni.org" }

Maui.Page {
    anchors.fill: parent
    showCSDControls: true
	
	StackLayout {
		id: projectViews
	}
	
	Overview {
		id: overview
		projectViews: projectViews
	}
	// keybinding to show the overview
}

// if first arg is "locked": read'only view, communicate with emergency accounts

// use lines on borders of scrolled QtQuick widgets to show the amount of overflowed content

}
