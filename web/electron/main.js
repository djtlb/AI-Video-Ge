/* eslint-disable */
const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
	const startUrl = process.env.ELECTRON_START_URL ||
		`file://${path.join(__dirname, '..', 'out', 'index.html')}`;

	mainWindow = new BrowserWindow({
		width: 1200,
		height: 800,
		webPreferences: {
			preload: path.join(__dirname, 'preload.js'),
			nodeIntegration: false,
			contextIsolation: true,
		},
	});

	mainWindow.loadURL(startUrl);

	mainWindow.on('closed', () => {
		mainWindow = null;
	});
}

app.whenReady().then(() => {
	createWindow();

	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) createWindow();
	});
});

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') app.quit();
});
