'use strict';

const path = require('path');
const url = require('url');
const {app, BrowserWindow} = require('electron');

let win;

function createWindow() {
    console.log("App finish loading, starting GUI...");

    win = new BrowserWindow({width: 400, height: 320});
    win.loadURL(url.format({
        pathname: path.join(__dirname, '..', 'templates', 'index.html'),
        protocol: 'file:',
        slashes: true
    }));

    win.on('close', () => {
        console.log("Exit -> close window");
        win = null;
    });

    win.once('ready-to-show', () => {
        console.log("Ready -> showing window");
        win.show();
    });
}

app.on('ready', createWindow);
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        console.log("Quiting app...");
        app.quit();
    }
});
app.on('activate', () => {
    if (win === null) {
        createWindow();
    }
});
