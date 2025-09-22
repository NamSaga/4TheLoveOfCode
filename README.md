# servr

**A simple linux tool for quickly serving local web files with a built-in HTTP server.**

![Web Server Launcher Screenshot](/utils/Screenshot.png)

## Features

- **Simple Web Server**: Quickly serve any local directory over HTTP
- **File Browser**: Navigate your files and directories easily
- **Recent Projects**: Quickly access your frequently used directories
- **Automatic Port Selection**: The app can find available ports if your preferred one is in use

## Installation

### From Source

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python web_server_launcher.py`

## Dependencies

- Python 3.6+
- PySide6 (Qt for Python)
- psutil

## Usage

1. **Select a Directory**: Click "Browse" to select the directory you want to serve
2. **Choose a Port**: Select a port number (default: 8000)
3. **Start the Server**: Click "Start Server" to begin serving files
4. **Open in Browser**: Click "Open in Browser" to view your site
5. **Navigate Files**: Double-click on files in the file list to open them in your browser
6. **Stop the Server**: Click "Stop Server" when you're done


## Motivation

I just wanted a tool for a lightweight HTTP server, the GUI was done good with the help of Coplilot, design inspired from Nvchad.
