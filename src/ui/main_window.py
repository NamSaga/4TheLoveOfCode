"""
Main Window Module
Contains the main application window and UI logic.
"""

import os
import signal
import webbrowser
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QListWidget,
    QSplitter, QFileDialog, QMessageBox, QSpinBox,
    QFrame, QListWidgetItem, QAbstractItemView, QStatusBar
)
from PySide6.QtCore import Qt

from ui.styles import NvimStyles
from server.server_thread import ServerThread
from utils.file_utils import FileUtils
from utils.project_manager import ProjectManager


class WebServerLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.server_port = 8000
        self.serve_directory = ""
        self.project_manager = ProjectManager()

        self.setup_ui()
        self.apply_nvim_theme()
        self.setup_signal_handlers()

        # Install event filter to capture all mouse clicks
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Event filter to capture all mouse press events and clear selections"""
        if event.type() == event.Type.MouseButtonPress:
            # Clear selections on any mouse click anywhere in the application
            self.recent_list.clearSelection()
            self.file_list.clearSelection()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Handle mouse press events to clear selections when clicking anywhere"""
        # Always clear selections from both list widgets when clicking anywhere
        self.recent_list.clearSelection()
        self.file_list.clearSelection()
        # Call the parent implementation
        super().mousePressEvent(event)

    def setup_ui(self):
        """Setup the Neovim-inspired user interface"""
        self.setWindowTitle("Web Server Launcher")
        self.setMinimumSize(900, 650)
        self.resize(1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main content area with splitter for responsive design
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (75% left, 25% right)
        splitter.setSizes([750, 250])
        splitter.setHandleWidth(1)

        # Status bar
        self.create_status_bar()

    def create_left_panel(self):
        """Create the main content panel with nvim-like styling"""
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #24283b;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Folder selection section
        folder_content = self.create_folder_content()
        left_layout.addWidget(folder_content)

        # Server configuration section
        config_content = self.create_config_content()
        left_layout.addWidget(config_content)

        # File preview section
        explorer_content = self.create_explorer_content()
        left_layout.addWidget(explorer_content)

        return left_widget

    def create_right_panel(self):
        """Create the control panel with nvim-like styling"""
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #1f2335;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Recent projects section
        recent_content = self.create_recent_content()
        right_layout.addWidget(recent_content)

        # Server control section
        control_content = self.create_control_content()
        right_layout.addWidget(control_content)

        # Server info section
        info_content = self.create_info_content()
        right_layout.addWidget(info_content)

        return right_widget

    def create_folder_content(self):
        """Create folder selection content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("FOLDER")
        label.setStyleSheet(NvimStyles.get_section_label_style())
        content_layout.addWidget(label)

        # Path input
        path_layout = QHBoxLayout()
        path_layout.setSpacing(6)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("~/projects/my-website")
        self.folder_input.setStyleSheet(NvimStyles.get_input_style())
        self.folder_input.setMinimumHeight(28)
        path_layout.addWidget(self.folder_input)

        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(NvimStyles.get_button_style("secondary"))
        browse_btn.setMinimumHeight(28)
        browse_btn.setMinimumWidth(70)
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)

        content_layout.addLayout(path_layout)
        return content_widget

    def create_config_content(self):
        """Create server configuration content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("CONFIG")
        label.setStyleSheet(NvimStyles.get_section_label_style())
        content_layout.addWidget(label)

        # Port configuration
        port_layout = QHBoxLayout()
        port_layout.setSpacing(6)

        port_label = QLabel("Port:")
        port_label.setStyleSheet(NvimStyles.get_regular_label_style())
        port_layout.addWidget(port_label)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1000, 65535)
        self.port_spinbox.setValue(8000)
        self.port_spinbox.setStyleSheet(NvimStyles.get_input_style())
        self.port_spinbox.setMinimumHeight(28)
        self.port_spinbox.setMaximumWidth(90)
        port_layout.addWidget(self.port_spinbox)

        port_layout.addStretch()
        content_layout.addLayout(port_layout)
        return content_widget

    def create_explorer_content(self):
        """Create file explorer content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("EXPLORER")
        label.setStyleSheet(NvimStyles.get_section_label_style())
        content_layout.addWidget(label)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(NvimStyles.get_list_style())
        content_layout.addWidget(self.file_list)

        return content_widget

    def create_recent_content(self):
        """Create recent projects content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")

        # Use absolute positioning for the label
        label = QLabel("RECENT", content_widget)
        label.setStyleSheet(NvimStyles.get_section_label_style())
        label.move(10, 5)

        # Main layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 30, 10, 12)
        content_layout.setSpacing(0)

        # Recent list
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet(NvimStyles.get_recent_list_style())

        # Add spacer before the list
        spacer = QWidget()
        spacer.setFixedHeight(8)
        content_layout.addWidget(spacer)

        self.recent_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.recent_list.setFixedHeight(110)
        self.recent_list.setFrameStyle(QFrame.NoFrame)
        self.recent_list.itemDoubleClicked.connect(self.use_recent_project)
        content_layout.addWidget(self.recent_list, 1)

        content_layout.addStretch(0)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        button_layout.setContentsMargins(0, 4, 0, 0)

        use_btn = QPushButton("Use")
        use_btn.setStyleSheet(NvimStyles.get_button_style("secondary"))
        use_btn.setFixedHeight(30)
        use_btn.clicked.connect(self.use_recent_project)
        button_layout.addWidget(use_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(NvimStyles.get_button_style("danger"))
        clear_btn.setFixedHeight(30)
        clear_btn.clicked.connect(self.clear_recent_projects)
        button_layout.addWidget(clear_btn)

        content_layout.addLayout(button_layout)
        return content_widget

    def create_control_content(self):
        """Create server control content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("ACTIONS")
        label.setStyleSheet(NvimStyles.get_section_label_style())
        content_layout.addWidget(label)

        self.start_btn = QPushButton("Start Server")
        self.start_btn.setStyleSheet(NvimStyles.get_button_style("primary"))
        self.start_btn.setMinimumHeight(32)
        self.start_btn.clicked.connect(self.start_server)
        content_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.setStyleSheet(NvimStyles.get_button_style("danger"))
        self.stop_btn.setMinimumHeight(28)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_server)
        content_layout.addWidget(self.stop_btn)

        self.open_btn = QPushButton("Open Browser")
        self.open_btn.setStyleSheet(NvimStyles.get_button_style("success"))
        self.open_btn.setMinimumHeight(28)
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_browser)
        content_layout.addWidget(self.open_btn)

        return content_widget

    def create_info_content(self):
        """Create server info content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("OUTPUT")
        label.setStyleSheet(NvimStyles.get_section_label_style())
        content_layout.addWidget(label)

        self.info_text = QTextEdit()
        self.info_text.setStyleSheet(NvimStyles.get_terminal_style())
        self.info_text.setReadOnly(True)
        self.info_text.setPlainText("""Web Server Launcher v2.0
Ready to serve local projects

Select a folder to get started...""")
        content_layout.addWidget(self.info_text)

        return content_widget

    def create_status_bar(self):
        """Create nvim-style status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addPermanentWidget(QLabel("Web Server Launcher"))
        self.status_bar.showMessage("Ready • Select folder to start")

    def apply_nvim_theme(self):
        """Apply Neovim/NvChad-inspired dark theme"""
        self.setStyleSheet(NvimStyles.get_main_window_style())

    def browse_folder(self):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Web Project Folder",
            self.serve_directory or os.path.expanduser("~")
        )

        if folder_path:
            self.folder_input.setText(folder_path)
            self.serve_directory = folder_path
            self.validate_folder(folder_path)
            self.show_folder_contents(folder_path)
            self.project_manager.add_recent_project(folder_path)
            self.update_recent_projects_display()

    def validate_folder(self, folder_path):
        """Validate the selected folder"""
        is_valid, message = FileUtils.validate_folder(folder_path)
        if not is_valid:
            self.update_status(message, "error")
        return is_valid

    def show_folder_contents(self, folder_path):
        """Display folder contents in the list"""
        self.file_list.clear()

        success, contents = FileUtils.get_folder_contents(folder_path)
        if success:
            for display_item in contents:
                list_item = QListWidgetItem(display_item)
                self.file_list.addItem(list_item)
        else:
            self.update_status(contents, "error")  # contents contains error message

    def start_server(self):
        """Start the HTTP server"""
        if not self.serve_directory:
            msg_box = self.create_styled_message_box("Warning", "Please select a folder to serve first.", "warning")
            msg_box.exec()
            return

        if not os.path.exists(self.serve_directory):
            msg_box = self.create_styled_message_box("Error", "Selected folder does not exist.", "error")
            msg_box.exec()
            return

        # Check if port is available
        if not FileUtils.is_port_available(self.port_spinbox.value()):
            msg_box = self.create_styled_message_box("Error", f"Port {self.port_spinbox.value()} is already in use.", "error")
            msg_box.exec()
            return

        self.server_port = self.port_spinbox.value()

        # Start server in thread
        self.server_thread = ServerThread(self.serve_directory, self.server_port)
        self.server_thread.status_update.connect(self.handle_server_status)
        self.server_thread.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_btn.setEnabled(True)

        self.update_status(f"Starting server on port {self.server_port}...", "info")

    def stop_server(self):
        """Stop the HTTP server"""
        if self.server_thread:
            self.server_thread.stop_server()
            self.server_thread.wait()
            self.server_thread = None

        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.open_btn.setEnabled(False)

        self.update_status("Server stopped", "info")

    def open_browser(self):
        """Open the server URL in default browser"""
        if self.server_thread and self.server_thread.isRunning():
            url = f"http://localhost:{self.server_port}"
            webbrowser.open(url)
            self.update_status(f"Opened {url} in browser", "success")
        else:
            msg_box = self.create_styled_message_box("Warning", "Server is not running.", "warning")
            msg_box.exec()

    def handle_server_status(self, message, status_type):
        """Handle server status updates"""
        self.update_status(message, status_type)

        if "started" in message.lower():
            server_info = f"""[SERVER ACTIVE]
─────────────────────────────────────────────────
Directory: {self.serve_directory}
URL:       http://localhost:{self.server_port}
Port:      {self.server_port}
Status:    Running

[CONTROLS]
─────────────────────────────────────────────────
• Browser opened automatically to HTML file
• Use 'Stop Server' button to terminate
• Share URL with others on your network

[LOG]
─────────────────────────────────────────────────
Server initialized successfully
Listening on localhost:{self.server_port}
Browser opened: http://localhost:{self.server_port}
            """
            self.info_text.setPlainText(server_info.strip())

            # Automatically open browser when server starts
            base_url = f"http://localhost:{self.server_port}"
            target_url = base_url

            # Try to find and open HTML files
            index_file = FileUtils.find_index_file(self.serve_directory)
            if index_file:
                target_url = f"{base_url}/{index_file}"

            try:
                webbrowser.open(target_url)
                if target_url != base_url:
                    filename = target_url.split('/')[-1]
                    self.update_status(f"Server started • Browser opened: {filename}", "success")
                else:
                    self.update_status(f"Server started • Browser opened: {base_url} (no HTML file found)", "warning")
            except Exception as e:
                self.update_status(f"Server started • Failed to open browser: {str(e)}", "warning")

    def update_status(self, message, status_type="info"):
        """Update status message with nvim-style colors"""
        prefixes = {
            "info": "●",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }

        prefix = prefixes.get(status_type, "●")
        self.status_bar.showMessage(f"{prefix} {message}")

    def update_recent_projects_display(self):
        """Update the recent projects list"""
        self.recent_list.clear()

        sorted_projects = self.project_manager.get_sorted_projects(10)

        for folder_path, count in sorted_projects:
            display_name = f"• {os.path.basename(folder_path)} ({count}x)"
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, folder_path)  # Store full path
            self.recent_list.addItem(item)

    def use_recent_project(self):
        """Use selected recent project"""
        current_item = self.recent_list.currentItem()
        if current_item:
            folder_path = current_item.data(Qt.UserRole)
            if folder_path and os.path.exists(folder_path):
                self.folder_input.setText(folder_path)
                self.serve_directory = folder_path
                self.validate_folder(folder_path)
                self.show_folder_contents(folder_path)
                self.update_status(f"Selected: {os.path.basename(folder_path)}", "success")
            else:
                msg_box = self.create_styled_message_box("Warning", "Selected project no longer exists.", "warning")
                msg_box.exec()
                self.update_recent_projects_display()

    def clear_recent_projects(self):
        """Clear recent projects history"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Clear History")
        msg_box.setText("Are you sure you want to clear the recent projects history?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet(NvimStyles.get_message_box_style())

        reply = msg_box.exec()

        if reply == QMessageBox.Yes:
            self.project_manager.clear_recent_projects()
            self.update_recent_projects_display()
            self.update_status("Recent projects cleared", "info")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            if self.server_thread:
                self.stop_server()
            from PySide6.QtWidgets import QApplication
            QApplication.quit()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def closeEvent(self, event):
        """Handle application close event"""
        if self.server_thread and self.server_thread.isRunning():
            msg_box = self.create_styled_message_box(
                "Server Running",
                "The server is still running. Stop it before closing?",
                "warning",
                QMessageBox.Yes | QMessageBox.No
            )
            msg_box.setDefaultButton(QMessageBox.Yes)
            reply = msg_box.exec()

            if reply == QMessageBox.Yes:
                self.stop_server()

        event.accept()

    def create_styled_message_box(self, title, text, icon_type="warning", buttons=None):
        """Create a styled message box that matches the main window theme"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        if buttons:
            msg_box.setStandardButtons(buttons)
        else:
            msg_box.setStandardButtons(QMessageBox.Ok)

        if buttons == (QMessageBox.Yes | QMessageBox.No):
            msg_box.setDefaultButton(QMessageBox.No)

        msg_box.setStyleSheet(NvimStyles.get_message_box_style())
        return msg_box
