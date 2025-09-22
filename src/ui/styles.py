"""
UI Styles Module
Contains all styling definitions for the Neovim/NvChad-inspired theme.
"""


class NvimStyles:
    """Neovim/NvChad-inspired styling definitions"""

    @staticmethod
    def get_main_window_style():
        """Get the main window and application-wide styling"""
        return """
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
        """

    @staticmethod
    def get_input_style():
        """Get nvim-style input styling - completely borderless"""
        return """
            QLineEdit, QSpinBox {
                background: transparent;
                border: none;
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
                outline: none;
            }
            QLineEdit:hover, QSpinBox:hover {
                background: transparent;
                border: none;
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

    @staticmethod
    def get_button_style(variant="primary"):
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

    @staticmethod
    def get_list_style():
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

    @staticmethod
    def get_terminal_style():
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

    @staticmethod
    def get_section_label_style():
        """Get section label styling"""
        return """
            color: #565f89;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """

    @staticmethod
    def get_regular_label_style():
        """Get regular label styling"""
        return """
            color: #c0caf5;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 12px;
            background: transparent;
        """

    @staticmethod
    def get_message_box_style():
        """Get styled message box that matches the main window theme"""
        return """
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
        """

    @staticmethod
    def get_recent_list_style():
        """Get recent projects list styling with reduced padding"""
        return """
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
                padding: 2px 12px;
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
        """
