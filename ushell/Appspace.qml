import QtQml.Models
import QtQuick
import QtQuick.Layouts

// when all windows are closed, open launcher

// appspaces
// create a quick stack each containing a modal view
// when a wayland surface appears, put it in the focused stack view
// if its the first one in the view, put it in stack, otherwise put it in the modal popup
// to close popup windows, press "super+space" or "alt+space"

Popup {
	property string name
	modal: true
	focus: true
}

// keybinding to close appspace
// Super+Escape
// Alt+Escape
Shortcut {
	sequence: "Alt+Backspace"
	onActivated: close_modal_windows();
}

// super/alt+<num>:
// if Application.screens[num] is not empty, just focus the screen, otherwise move the current window along,
// and store its appid and title, in ~/.config/ushell/screens
// super/alt+0 removes the window from the screen and the config file