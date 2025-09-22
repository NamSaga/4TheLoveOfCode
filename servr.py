#!/usr/bin/env python3
"""
Local Web Server Launcher - Modern Desktop Application
A sleek, responsive GUI application to serve local web builds with ease.
Built with PySide6.
"""

import sys
import os
import json
import subprocess
import webbrowser
import threading
import time
import socket
import signal
import psutil
from pathlib import Path

# Check for PySide6 and provide helpful error message
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QGridLayout, QPushButton, QLineEdit, QLabel, QTextEdit, QListWidget,
        QGroupBox, QSplitter, QFileDialog, QMessageBox, QSpinBox,
        QFrame, QSizePolicy, QListWidgetItem, QAbstractItemView, QStatusBar
    )
    from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
    from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
    PYSIDE6_AVAILABLE = True
except ImportError as e:
    PYSIDE6_AVAILABLE = False
    print("=" * 60)
    print("⚠ PySide6 is required for the modern GUI interface!")
    print("=" * 60)
    print()
    print("To install PySide6, run one of these commands:")
    print("  • pip install PySide6")
    print("  • python3 -m pip install PySide6")
    print("  • sudo apt install python3-pyside6 (on Ubuntu/Debian)")
    print()
    print("After installation, run this program again.")
    print()
    print("=" * 60)
    print(f"Error details: {e}")
    sys.exit(1)


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


class WebServerLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.server_port = 8000
        self.serve_directory = ""
        self.recent_projects_file = os.path.expanduser("~/.web_server_launcher_recent.json")
        self.recent_projects = self.load_recent_projects()
        
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
        self.setWindowTitle("servr")
        # More compact window size for NvChad-style compactness
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
        
        # Set splitter proportions (75% left, 25% right) - more space for content
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

        # Folder selection section - no box, just content
        folder_content = self.create_folder_content()
        left_layout.addWidget(folder_content)

        # Server configuration section - no box, just content
        config_content = self.create_config_content()
        left_layout.addWidget(config_content)

        # File preview section - no box, just content
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

        # Recent projects section - no box, just content
        recent_content = self.create_recent_content()
        right_layout.addWidget(recent_content)

        # Server control section - no box, just content
        control_content = self.create_control_content()
        right_layout.addWidget(control_content)

        # Server info section - no box, just content
        info_content = self.create_info_content()
        right_layout.addWidget(info_content)

        return right_widget

    def create_folder_content(self):
        """Create folder selection content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        # More compact margins for NvChad-style density
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("FOLDER")
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(label)

        # Path input
        path_layout = QHBoxLayout()
        path_layout.setSpacing(6)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("~/projects/my-web-build")
        self.folder_input.setStyleSheet(self.get_nvim_input_style())
        self.folder_input.setMinimumHeight(28)  # Reduced height
        path_layout.addWidget(self.folder_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(self.get_nvim_button_style("secondary"))
        browse_btn.setMinimumHeight(28)  # Reduced height
        browse_btn.setMinimumWidth(70)   # Slightly narrower
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        content_layout.addLayout(path_layout)
        return content_widget

    def create_config_content(self):
        """Create server configuration content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        # More compact margins for NvChad-style density
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("CONFIG")
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(label)

        # Port configuration
        port_layout = QHBoxLayout()
        port_layout.setSpacing(6)

        port_label = QLabel("Port:")
        port_label.setStyleSheet("""
            color: #c0caf5;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 12px;
            background: transparent;
        """)
        port_layout.addWidget(port_label)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1000, 65535)
        self.port_spinbox.setValue(8000)
        self.port_spinbox.setStyleSheet(self.get_nvim_input_style())
        self.port_spinbox.setMinimumHeight(28)  # Reduced height
        self.port_spinbox.setMaximumWidth(90)  # Slightly narrower
        port_layout.addWidget(self.port_spinbox)

        port_layout.addStretch()
        content_layout.addLayout(port_layout)
        return content_widget

    def create_explorer_content(self):
        """Create file explorer content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #24283b;")
        content_layout = QVBoxLayout(content_widget)
        # More compact margins for NvChad-style density
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("EXPLORER")
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(label)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(self.get_nvim_list_style())
        content_layout.addWidget(self.file_list)

        return content_widget

    def create_recent_content(self):
        """Create recent projects content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")

        # Use absolute positioning for the label to ensure fixed position
        label = QLabel("RECENT", content_widget)
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        # Position label at the top of the section, aligned with other labels
        label.move(10, 5)  # x=10 (same as margin), y=5 (higher position)
        # Recent label
        # Main layout - with adjusted top margin to account for absolute positioned label
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 30, 10, 12)  # Increased top margin to move list lower
        content_layout.setSpacing(0)  # No spacing to position list immediately after label

        # Recent list with fixed position relative to the label
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 2px 12px; /* Reduced vertical padding to compact items */
                border-radius: 0px;
                margin: 0px;
                text-align: left;
            }
            QListWidget::item:selected {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
            QListWidget::item:hover {
                background-color: #3c4048;
            }
        """)

        # Add spacer before the list to push it down further
        spacer = QWidget()
        spacer.setFixedHeight(8)  # Add extra space at the top
        content_layout.addWidget(spacer)

        # Fix height to prevent stretching, matching explorer style
        self.recent_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.recent_list.setFixedHeight(110)  # Use fixed height instead of maximum
        self.recent_list.setFrameStyle(QFrame.NoFrame)  # Remove any frame
        self.recent_list.itemDoubleClicked.connect(self.use_recent_project)
        content_layout.addWidget(self.recent_list, 1)  # Give it stretch factor of 1

        # Add spacer to maintain fixed positioning
        content_layout.addStretch(0)

        # Buttons - position them with fixed heights
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        button_layout.setContentsMargins(0, 4, 0, 0)  # Small top margin from list

        use_btn = QPushButton("Use")
        use_btn.setStyleSheet(self.get_nvim_button_style("secondary"))
        use_btn.setFixedHeight(30)  # Enforce fixed height
        use_btn.clicked.connect(self.use_recent_project)
        button_layout.addWidget(use_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(self.get_nvim_button_style("danger"))
        clear_btn.setFixedHeight(30)  # Enforce fixed height
        clear_btn.clicked.connect(self.clear_recent_projects)
        button_layout.addWidget(clear_btn)

        content_layout.addLayout(button_layout)
        return content_widget

    def create_control_content(self):
        """Create server control content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")
        content_layout = QVBoxLayout(content_widget)
        # More compact margins for NvChad-style density
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("ACTIONS")
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(label)

        self.start_btn = QPushButton("Start Server")
        self.start_btn.setStyleSheet(self.get_nvim_button_style("primary"))
        self.start_btn.setMinimumHeight(32)  # Reduced height
        self.start_btn.clicked.connect(self.start_server)
        content_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.setStyleSheet(self.get_nvim_button_style("danger"))
        self.stop_btn.setMinimumHeight(28)  # Reduced height
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_server)
        content_layout.addWidget(self.stop_btn)

        self.open_btn = QPushButton("Open Browser")
        self.open_btn.setStyleSheet(self.get_nvim_button_style("success"))
        self.open_btn.setMinimumHeight(28)  # Reduced height
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_browser)
        content_layout.addWidget(self.open_btn)

        return content_widget

    def create_info_content(self):
        """Create server info content"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f2335;")
        content_layout = QVBoxLayout(content_widget)
        # More compact margins for NvChad-style density
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(8)

        # Section label
        label = QLabel("OUTPUT")
        label.setStyleSheet("""
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(label)

        self.info_text = QTextEdit()
        self.info_text.setStyleSheet(self.get_nvim_terminal_style())
        self.info_text.setReadOnly(True)
        self.info_text.setPlainText("""Ready to serve local projects

Select a folder to get started...""")
        content_layout.addWidget(self.info_text)

        return content_widget

    def create_status_bar(self):
        """Create nvim-style status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Display simple message on the right side
        self.status_bar.addPermanentWidget(QLabel("servr"))

        self.status_bar.showMessage("Ready • Select folder to start")

    def apply_nvim_theme(self):
        """Apply Neovim/NvChad-inspired dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QWidget {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QSplitter::handle {
                background-color: #3c4048;
                width: 1px;
                height: 1px;
            }
            /* Flat scroll bar styling - completely remove corner boxes */
            QScrollBar:vertical {
                border: none;
                background: #16161e;
                width: 10px;
                margin: 0px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3c4048;
                min-height: 20px;
                border-radius: 0px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background: #565f89;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: transparent;
                border: none;
                height: 0px;
                width: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
            /* Horizontal scrollbar */
            QScrollBar:horizontal {
                border: none;
                background: #16161e;
                height: 10px;
                margin: 0px;
                border-radius: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #3c4048;
                min-width: 20px;
                border-radius: 0px;
                border: none;
            }
            QScrollBar::handle:horizontal:hover {
                background: #565f89;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
            }
            /* Completely remove corner intersection */
            QScrollBar::corner {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
                margin: 0px;
                padding: 0px;
            }
            QAbstractScrollArea::corner {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)
        
    def get_nvim_input_style(self):
        """Get nvim-style input styling - completely borderless"""
        return """
            QLineEdit, QSpinBox {
                background: transparent;
                border: none;
                /*border-bottom: 1px solid #3c4048;*/
                border-radius: 0px;
                padding: 8px 12px;
                color: #c0caf5;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                selection-background-color: #7aa2f7;
                outline: none;
            }
            QLineEdit:focus, QSpinBox:focus {
                background: transparent;
                border: none;
                /*border-bottom: 1px solid #3c4048;*/
                outline: none;
            }
            QLineEdit:hover, QSpinBox:hover {
                background: transparent;
                border: none;
                /*border-bottom: 1px solid #565f89;*/
                outline: none;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                background-color: #3c4048;
                border: none;
                color: #c0caf5;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #565f89;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                color: #c0caf5;
                width: 8px;
                height: 8px;
            }
        """
        
    def get_nvim_button_style(self, variant="primary"):
        """Get nvim-style button styling - completely flat"""
        styles = {
            "primary": """
                QPushButton {
                    background-color: #7aa2f7;
                    color: #1a1b26;
                    border: none;
                    border-radius: 0px;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 16px;
                }
                QPushButton:hover {
                    background-color: #7dcfff;
                }
                QPushButton:pressed {
                    background-color: #6183bb;
                }
                QPushButton:disabled {
                    background-color: #3c4048;
                    color: #737aa2;
                }
            """,
            "secondary": """
                QPushButton {
                    background-color: #3c4048;
                    color: #c0caf5;
                    border: none;
                    border-radius: 0px;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                    font-size: 13px;
                    padding: 10px 16px;
                }
                QPushButton:hover {
                    background-color: #565f89;
                }
                QPushButton:pressed {
                    background-color: #2a2e36;
                }
            """,
            "success": """
                QPushButton {
                    background-color: #9ece6a;
                    color: #1a1b26;
                    border: none;
                    border-radius: 0px;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 16px;
                }
                QPushButton:hover {
                    background-color: #b9f27c;
                }
                QPushButton:disabled {
                    background-color: #3c4048;
                    color: #737aa2;
                }
            """,
            "danger": """
                QPushButton {
                    background-color: #f7768e;
                    color: #1a1b26;
                    border: none;
                    border-radius: 0px;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 16px;
                }
                QPushButton:hover {
                    background-color: #ff9faa;
                }
                QPushButton:disabled {
                    background-color: #3c4048;
                    color: #737aa2;
                }
            """
        }
        return styles.get(variant, styles["primary"])
        
    def get_nvim_list_style(self):
        """Get nvim-style list widget styling - completely flat"""
        return """
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                border-radius: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
            QListWidget::item:hover {
                background-color: #3c4048;
            }
        """
        
    def get_nvim_terminal_style(self):
        """Get nvim-style terminal/output area styling - completely borderless"""
        return """
            QTextEdit {
                background-color: #16161e;
                border: none;
                border-radius: 0px;
                padding: 12px;
                color: #c0caf5;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.4;
                selection-background-color: #7aa2f7;
                selection-color: #1a1b26;
            }
        """
        
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
            self.add_recent_project(folder_path)
            
    def validate_folder(self, folder_path):
        """Validate the selected folder"""
        if not os.path.exists(folder_path):
            self.update_status("Selected folder does not exist", "error")
            return False
            

        
    def show_folder_contents(self, folder_path):
        """Display folder contents in the list"""
        self.file_list.clear()
        
        try:
            items = os.listdir(folder_path)
            items.sort()
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    display_item = f"▸ {item}/"
                else:
                    # Add file icons based on extension
                    ext = os.path.splitext(item)[1].lower()
                    icon = self.get_file_icon(ext)
                    display_item = f"{icon} {item}"
                
                list_item = QListWidgetItem(display_item)
                self.file_list.addItem(list_item)
                
        except Exception as e:
            self.update_status(f"Error reading folder: {str(e)}", "error")
            
    def get_file_icon(self, extension):
        """Get flat web-style icon for file type"""
        icons = {
            '.html': '◯', '.htm': '◯',
            '.css': '◆', '.js': '◈',
            '.json': '▣', '.xml': '▣',
            '.png': '▦', '.jpg': '▦', '.jpeg': '▦', '.gif': '▦',
            '.svg': '◇', '.ico': '▦',
            '.md': '▤', '.txt': '▤',
            '.py': '◐', '.php': '◑',
            '.zip': '▦', '.tar': '▦', '.gz': '▦',
            '.ts': '◈', '.tsx': '◈',
            '.vue': '◇', '.scss': '◆',
            '.sass': '◆', '.less': '◆'
        }
        return icons.get(extension, '▢')

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
        if not self.is_port_available(self.port_spinbox.value()):
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

    def is_port_available(self, port):
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
            
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

            # Try to find and open HTML files in priority order
            # First try common index files
            index_files = ['index.html', 'index.htm', 'default.html', 'home.html']
            found_index = False

            for index_file in index_files:
                index_path = os.path.join(self.serve_directory, index_file)
                if os.path.exists(index_path):
                    target_url = f"{base_url}/{index_file}"
                    found_index = True
                    break

            # If no standard index file found, look for any HTML file
            if not found_index:
                try:
                    html_files = []
                    for item in os.listdir(self.serve_directory):
                        if item.lower().endswith(('.html', '.htm')):
                            html_files.append(item)

                    if html_files:
                        # Sort HTML files and pick the first one (alphabetically)
                        html_files.sort()
                        target_url = f"{base_url}/{html_files[0]}"
                        found_index = True

                except Exception:
                    pass  # If we can't read directory, fall back to base URL

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
        status_colors = {
            "info": "#7aa2f7",
            "success": "#9ece6a",
            "warning": "#e0af68",
            "error": "#f7768e"
        }

        # Map status types to nvim-style prefixes
        prefixes = {
            "info": "●",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }
        
        color = status_colors.get(status_type, status_colors["info"])
        prefix = prefixes.get(status_type, "●")

        self.status_bar.showMessage(f"{prefix} {message}")

    def load_recent_projects(self):
        """Load recent projects from file"""
        try:
            if os.path.exists(self.recent_projects_file):
                with open(self.recent_projects_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
        
    def save_recent_projects(self):
        """Save recent projects to file"""
        try:
            with open(self.recent_projects_file, 'w') as f:
                json.dump(self.recent_projects, f, indent=2)
        except Exception:
            pass
            
    def add_recent_project(self, folder_path):
        """Add or update a project in recent projects"""
        if folder_path in self.recent_projects:
            self.recent_projects[folder_path] += 1
        else:
            self.recent_projects[folder_path] = 1
        self.save_recent_projects()
        self.update_recent_projects_display()
        
    def update_recent_projects_display(self):
        """Update the recent projects list"""
        self.recent_list.clear()
        
        # Sort by usage count (most used first)
        sorted_projects = sorted(self.recent_projects.items(), key=lambda x: x[1], reverse=True)
        
        for folder_path, count in sorted_projects[:10]:  # Show top 10
            if os.path.exists(folder_path):
                display_name = f"• {os.path.basename(folder_path)} ({count}x)"
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, folder_path)  # Store full path
                self.recent_list.addItem(item)
            else:
                # Remove non-existent paths
                del self.recent_projects[folder_path]
                
        if sorted_projects:
            self.save_recent_projects()
            
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
        # Create custom styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Clear History")
        msg_box.setText("Are you sure you want to clear the recent projects history?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # Apply custom styling to match main window theme
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1b26;
                color: #c0caf5;
                border: none;
            }
            QMessageBox QLabel {
                color: #c0caf5;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                background: transparent;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #3c4048;
                color: #c0caf5;
                border: none;
                border-radius: 0px;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 8px 16px;
                margin: 4px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #565f89;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a2e36;
            }
            QMessageBox QPushButton:default {
                background-color: #7aa2f7;
                color: #1a1b26;
                font-weight: bold;
            }
            QMessageBox QPushButton:default:hover {
                background-color: #7dcfff;
            }
        """)

        reply = msg_box.exec()

        if reply == QMessageBox.Yes:
            self.recent_projects = {}
            self.save_recent_projects()
            self.update_recent_projects_display()
            self.update_status("Recent projects cleared", "info")
            
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            if self.server_thread:
                self.stop_server()
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

        # Remove window frame and borders
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        if buttons:
            msg_box.setStandardButtons(buttons)
        else:
            msg_box.setStandardButtons(QMessageBox.Ok)

        # Set default button based on type
        if buttons == (QMessageBox.Yes | QMessageBox.No):
            msg_box.setDefaultButton(QMessageBox.No)

        # Apply custom styling to match main window theme - no borders
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1b26;
                color: #c0caf5;
                border: none;
                border-radius: 0px;
            }
            QMessageBox QLabel {
                color: #c0caf5;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                background: transparent;
                padding: 15px;
            }
            QMessageBox QPushButton {
                background-color: #3c4048;
                color: #c0caf5;
                border: none;
                border-radius: 0px;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 8px 16px;
                margin: 4px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #565f89;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a2e36;
            }
            QMessageBox QPushButton:default {
                background-color: #7aa2f7;
                color: #1a1b26;
                font-weight: bold;
            }
            QMessageBox QPushButton:default:hover {
                background-color: #7dcfff;
            }
        """)

        return msg_box

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("servr")
    app.setApplicationVersion("1.9")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = WebServerLauncher()
    window.show()
    
    # Update recent projects on startup
    window.update_recent_projects_display()

    # Execute the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
