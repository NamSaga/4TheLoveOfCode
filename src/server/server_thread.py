"""
Server Thread Module
Handles HTTP server operations in a separate thread.
"""

import subprocess
from PySide6.QtCore import QThread, Signal


class ServerThread(QThread):
    """Thread for running the HTTP server"""
    status_update = Signal(str, str)  # message, status_type

    def __init__(self, directory, port):
        super().__init__()
        self.directory = directory
        self.port = port
        self.server_process = None

    def run(self):
        try:
            cmd = ["python3", "-m", "http.server", str(self.port)]
            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.status_update.emit(f"Server started on port {self.port}", "success")

            # Wait for the process to complete or be terminated
            self.server_process.wait()

        except Exception as e:
            self.status_update.emit(f"Error starting server: {str(e)}", "error")

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.status_update.emit("Server stopped", "info")
