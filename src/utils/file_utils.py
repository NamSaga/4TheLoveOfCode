"""
File Utilities Module
Handles file operations, validation, and file type detection.
"""

import os
import socket


class FileUtils:
    """Utility functions for file operations"""

    @staticmethod
    def get_file_icon(extension):
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

    @staticmethod
    def validate_folder(folder_path):
        """Validate the selected folder"""
        if not os.path.exists(folder_path):
            return False, "Selected folder does not exist"
        if not os.path.isdir(folder_path):
            return False, "Selected path is not a directory"
        return True, "Folder is valid"

    @staticmethod
    def get_folder_contents(folder_path):
        """Get folder contents with icons"""
        try:
            items = os.listdir(folder_path)
            items.sort()

            contents = []
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    display_item = f"▸ {item}/"
                else:
                    ext = os.path.splitext(item)[1].lower()
                    icon = FileUtils.get_file_icon(ext)
                    display_item = f"{icon} {item}"
                contents.append(display_item)

            return True, contents
        except Exception as e:
            return False, f"Error reading folder: {str(e)}"

    @staticmethod
    def find_index_file(directory):
        """Find the best index file to open in browser"""
        # Try to find common index files in priority order
        index_files = ['index.html', 'index.htm', 'default.html', 'home.html']

        for index_file in index_files:
            index_path = os.path.join(directory, index_file)
            if os.path.exists(index_path):
                return index_file

        # If no standard index file found, look for any HTML file
        try:
            html_files = []
            for item in os.listdir(directory):
                if item.lower().endswith(('.html', '.htm')):
                    html_files.append(item)

            if html_files:
                # Sort HTML files and pick the first one (alphabetically)
                html_files.sort()
                return html_files[0]
        except Exception:
            pass

        return None

    @staticmethod
    def is_port_available(port):
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
