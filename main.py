#!/usr/bin/env python3
"""
Local Web Server Launcher - Main Entry Point
A sleek, responsive GUI application to serve local web builds with ease.
Built with PySide6.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check for PySide6 and provide helpful error message
try:
    from PySide6.QtWidgets import QApplication
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

from ui.main_window import WebServerLauncher


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("servr")
    app.setApplicationVersion("1.9.0")
    app.setOrganizationName("servr")
    app.setOrganizationDomain("servr.app")

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
