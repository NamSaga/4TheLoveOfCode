"""
Project Manager Module
Handles recent projects storage and management.
"""

import os
import json


class ProjectManager:
    """Manages recent projects functionality"""

    def __init__(self):
        self.recent_projects_file = os.path.expanduser("~/.web_server_launcher_recent.json")
        self.recent_projects = self.load_recent_projects()

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

    def get_sorted_projects(self, max_count=10):
        """Get recent projects sorted by usage count"""
        # Sort by usage count (most used first)
        sorted_projects = sorted(self.recent_projects.items(), key=lambda x: x[1], reverse=True)

        # Filter out non-existent paths and return only existing ones
        valid_projects = []
        for folder_path, count in sorted_projects[:max_count]:
            if os.path.exists(folder_path):
                valid_projects.append((folder_path, count))
            else:
                # Remove non-existent paths
                del self.recent_projects[folder_path]

        # Save after cleanup
        if len(valid_projects) != len(sorted_projects[:max_count]):
            self.save_recent_projects()

        return valid_projects

    def clear_recent_projects(self):
        """Clear recent projects history"""
        self.recent_projects = {}
        self.save_recent_projects()
