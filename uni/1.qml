#!/usr/bin/env qml6

// if first arg is "locked": read'only view, communicate with emergency accounts

// use lines on borders of scrolled QtQuick widgets to show the amount of overflowed content

/*
create an app with appId "uni"
app.onActivate(function(app) {
	switch (app.getWindows()[0]) {
		null =>
			projectViews = new Stack();
			
			overview = Overview(projectViews);
			
			rootView = new Overlay();
			rootView.add(projectViews);
			rootView.addOverlay(overview);
			// keybinding to show the overview
			
			window = new ApplicationWindow({
				application: app,
				maximized: true,
				titlebar: null
			});
			window.setChild(rootView)
			
			// set keybinding to show the overview
		
		win => win.present()
	}
})
*/
