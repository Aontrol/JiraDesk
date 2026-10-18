JiraDesk — Personal Workflow Tracker
JiraDesk is a lightweight desktop application for managing personal tasks and projects. Built with Python, Tkinter, and SQLite, it provides a simple way to organize issues, track progress, and record working hours without relying on cloud services.

The application runs locally on Windows and features a clean, minimalist interface inspired by Google's Material Design.

Features
Interface and Design
Clean interface with a white background, blue accents, subtle borders, and readable typography.
High-DPI display support for Windows.
Color-coded issue types, priorities, and workflow statuses.
Simple layouts designed for everyday task management.
Kanban Board
Five workflow columns: Backlog, To Do, In Progress, In Review, and Done.
Live issue counts for each column.
Quick issue creation directly from the board.
Previous and next status buttons on issue cards.
Right-click context menu for moving issues to any status.
Empty-state messages for columns without issues.
Scrollable board with mouse wheel support.
Backlog and List View
Tabular view built with ttk.Treeview.
Sortable columns for issue key, summary, priority, status, and logged hours.
Instant search and filtering.
Clear search functionality for quickly returning to the full issue list.
Issue Management
Create, edit, and manage tasks, bugs, stories, and epics.
Support for multiple projects with custom issue prefixes, such as DEV-101, APP-24, and LIFE-7.
Built-in time tracking with hours, minutes, and worklog notes.
Work history associated with individual issues.
Project deletion safeguards.
Data Management
JiraDesk includes built-in tools for managing local workspace data.

Database backup: Create consistent SQLite database backups.
Restore backup: Restore a workspace from an existing backup.
JSON export: Export projects, issues, and worklogs to a portable JSON file.
Start fresh: Clear workspace data, with an opportunity to back up existing data first.
Reset sample data: Restore the default demonstration projects and tasks.
Keyboard Shortcuts

Shortcut	Action
Ctrl + N	Create a new issue
Ctrl + F	Focus the search bar
F5	Refresh the board
Ctrl + Enter	Save an issue or project in supported dialogs
Escape	Close or cancel a dialog
Getting Started
Requirements
Windows
Python 3 with Tkinter support
No additional runtime packages required for normal application use
Run the Application
Option 1: Using the Windows launcher

Double-click start.bat to launch JiraDesk.

Option 2: Launch without a console window

Double-click start_silent.vbs to start the application without displaying a command prompt window.

Option 3: Using the command line

Open a terminal in the project directory and run:


python main.py
Building a Standalone Executable
JiraDesk includes an automated build script for packaging the application with PyInstaller.

Run build_exe.bat to check for PyInstaller, install it if necessary, and build the application.

The build produces two versions:

dist\JiraDesk_Portable.exe — a single-file executable.
dist\JiraDesk\JiraDesk.exe — an executable with its supporting files.
The generated builds can run without requiring a separate Python installation on the target machine, provided the appropriate executable and bundled files are included.

Building the Windows Installer
Run build_installer.bat to build the executable and create a Windows installer using Inno Setup.

The installer supports:

A standard Windows installation wizard.
Desktop shortcuts.
Start Menu shortcuts.
Uninstallation through Windows settings.
The installer output is saved to:


Output\JiraDesk_Setup_v1.0.exe
Inno Setup must be installed for the installer-generation step. If it is unavailable, the standalone executable builds can still be produced.

Download Inno Setup from the official website:

https://jrsoftware.org/isdl.php

Project Structure

JiraDesk/
├── main.py
├── database.py
├── models.py
├── theme.py
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── kanban_view.py
│   ├── table_view.py
│   ├── card_widget.py
│   ├── issue_dialog.py
│   └── project_dialog.py
├── assets/
│   ├── app_icon.ico
│   └── app_icon.png
├── start.bat
├── start_silent.vbs
├── build_exe.bat
├── build_installer.bat
├── installer.iss
├── requirements.txt
└── README.md
Architecture

File	Responsibility
main.py	Application entry point and Windows display scaling
database.py	SQLite operations, backups, restoration, and data management
models.py	Data models for projects, issues, statuses, and worklogs
theme.py	Colors, typography, and interface styles
ui/app.py	Main window, toolbar, search, and data-management menu
ui/kanban_view.py	Kanban board and workflow columns
ui/table_view.py	Sortable backlog and list view
ui/card_widget.py	Issue cards and status controls
ui/issue_dialog.py	Issue creation, editing, and worklog entry
ui/project_dialog.py	Project creation dialog
Data Storage
JiraDesk stores its workspace data in a local SQLite database named jira_tracker.db. The database is created automatically when needed.

All projects, issues, and worklogs are managed locally. Data is not automatically uploaded to a remote server.

The Data & Backup menu provides access to database backups, restoration, JSON export, and workspace reset options.

Users should keep backups in a separate location to protect against accidental deletion or hardware failure.

Technologies Used
Python — application logic.
Tkinter and ttk — desktop interface.
SQLite — local database.
PyInstaller — standalone executable packaging.
Inno Setup — Windows installer creation.
Design Goals
JiraDesk is designed around a few practical goals:

Keep personal task management simple.
Store data locally and work offline.
Make task status changes quick and intuitive.
Provide straightforward backup and recovery options.
Avoid unnecessary runtime dependencies.
License
Choose and add a license file before distributing JiraDesk publicly. Until a license is specified, the repository's reuse and redistribution terms remain undefined.