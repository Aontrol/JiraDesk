"""
JiraDesk — Personal Workflow Tracker
Main Application Entry Point.
"""
import sys
import os

if sys.platform == "win32":
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui.app import JiraDeskApp


def main():
    app = JiraDeskApp()
    app.mainloop()


if __name__ == "__main__":
    main()
