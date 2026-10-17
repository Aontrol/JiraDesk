# JiraDesk — Personal Workflow Tracker

> A lightweight, offline-first personal Jira desktop application built with Python, Tkinter, and SQLite, styled with Google's Minimalist Material Design.

---

## ✨ Features & Polish

- **Google Minimalist Material Design**: Clean white cards, Google Blue (`#1a73e8`) accents, subtle borders (`#dadce0`), crisp typography with Windows High-DPI support, and color-coded status chips with type icons (📋 Task, 🐛 Bug, 🚀 Story, ⚡ Epic) and priority dots (🟢, 🔵, 🟠, 🔴).
- **Interactive Multi-Column Kanban Board**: Visual status columns (`Backlog`, `To Do`, `In Progress`, `In Review`, `Done`) with live issue counters, quick "+ Add" buttons, empty-state placeholders, and flicker-free hover.
- **1-Click Status Transitions**: Intuitive `◀` and `▶` one-click buttons directly on each card to effortlessly advance or move tasks backward without menu hunting, plus a right-click context menu for direct jumps.
- **Tabular Backlog / List View**: Full data table powered by `ttk.Treeview` with clickable column headers for interactive ascending/descending sorting across Key, Summary, Priority, Status, and Logged Hours.
- **Complete Data Management (Backup, Restore & Reset)**:
  - **📁 Backup Database**: Create atomic live `.db` backups with a single click.
  - **📥 Restore from Backup**: Easily load and verify prior workspace backups.
  - **📤 Export All Data (JSON)**: Export projects, issues, and worklogs in portable JSON.
  - **⚠️ Start Fresh**: Clear all data to start with a clean, blank workspace ready for your personal tasks (with automated backup prompt).
  - **🔄 Reset to Sample Data**: Restore the default demonstration board and starter tasks anytime.
- **Workspace Project Management**: Support for multiple projects with custom prefix keys (e.g., `DEV-101`, `APP-24`, `LIFE-7`) and safe deletion guards.
- **Built-in Time Tracking & Worklogs**: Log hours and minutes directly inside any issue (or upon creating new issues) with notes and work history.
- **Live Instant Search**: Filter cards and backlog rows in real-time with an instant clear `✕` button.
- **Keyboard Shortcuts**:
  - `Ctrl + N`: Create new issue
  - `Ctrl + F`: Jump to search bar
  - `F5`: Refresh board
  - `Ctrl + Enter` (in dialogs): Save issue or project
  - `Escape` (in dialogs): Close / Cancel
- **Zero External Runtime Dependencies**: Uses Python's standard library (`tkinter` and `sqlite3`), bundled by default with Python on Windows.

---

## 🚀 One-Click Launch Options (Windows)

1. **One-Click Launch (`start.bat`)**:
   - Double-click `start.bat`. It will locate Python on your system and launch JiraDesk immediately.
2. **Zero-Console Silent Launch (`start_silent.vbs`)**:
   - Double-click `start_silent.vbs` to launch JiraDesk cleanly with zero command prompt window.
3. **Command Line Launch**:
   ```bash
   python main.py
   ```

---

## 🛠️ Automated Executable & Inno Setup Builder

Everything is automated so you don't need to manually configure build parameters:

### 1. Build Standalone `.EXE` (`build_exe.bat`)
- Double-click `build_exe.bat`.
- The script automatically checks for `pyinstaller`, installs it if missing via `pip`, and compiles:
  - **Portable Single-File App**: `dist\JiraDesk_Portable.exe` (run it anywhere without installation)
  - **Directory App**: `dist\JiraDesk\JiraDesk.exe`

### 2. Build Inno Setup Windows Installer (`build_installer.bat`)
- Double-click `build_installer.bat`.
- The script compiles the executable with PyInstaller, automatically scans your system for the Inno Setup compiler (`ISCC.exe`), and builds a professional Windows Setup Wizard:
  - **Output Installer**: `Output\JiraDesk_Setup_v1.0.exe`
  - Features: Desktop shortcut, Start Menu folder, clean uninstaller in Windows Control Panel.
- *Note*: If you don't have Inno Setup installed, download the free lightweight setup compiler from [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php). Your standalone executables will still be ready in `dist\` regardless.

---

## 📁 Project Architecture

```
JiraDesk/
├── main.py                  # App entry point with Windows High-DPI awareness
├── database.py              # SQLite engine with backup, restore, reset, & CRUD
├── models.py                # Dataclasses: Project, Issue, Status, Worklog
├── theme.py                 # Google Material theme constants, ttk styles, color schemes
├── ui/
│   ├── __init__.py
│   ├── app.py               # Main window, header toolbar, data & backup menu, search
│   ├── kanban_view.py       # Multi-column scrollable Kanban board with mouse wheel & empty states
│   ├── table_view.py        # Backlog list view with interactive column sorting
│   ├── card_widget.py       # Material issue card with 1-click move buttons & hover polish
│   ├── issue_dialog.py      # Modal dialog for creating/editing issues & worklogs
│   └── project_dialog.py    # Modal dialog for creating new workspace projects
├── assets/
│   ├── app_icon.ico         # High-resolution multi-size Windows icon
│   └── app_icon.png         # High-resolution PNG icon
├── start.bat                # One-click Windows runner
├── start_silent.vbs         # Silent zero-console VBScript launcher
├── build_exe.bat            # Automated PyInstaller build script
├── build_installer.bat      # Master automated script (PyInstaller + Inno Setup)
├── installer.iss            # Inno Setup 5/6 script with shortcuts & uninstaller
├── requirements.txt         # Dependency documentation
└── README.md                # Comprehensive documentation
```

---

## 💾 Database & Storage

All workflow data is stored locally in an embedded SQLite database (`jira_tracker.db`) created automatically in the application directory. Live atomic backups can be exported or restored anytime via the **⚙ Data & Backup** menu.
