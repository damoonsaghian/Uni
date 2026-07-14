// https://api.kde.org/mauikit/index.html

// https://doc.qt.io/qt-6/qtremoteobjects-index.html

// start in lock mode
// lock after 10m idle, if lock inhibit is not active
// before lock, show a 10s countdown screen

// lock mode: read'only view, comminicate with emergency accounts

// use lines on borders of scrolled QtQuick widgets to show the amount of overflowed content

// gnunet-arm -s -i fs

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
