"""
Google Minimalist Material Design Theme & UI Component Helpers for JiraDesk.
Provides consistent colors, typography, TTK styling, focus rings, window centering, and icon setup.
"""
import os
import tkinter as tk
from tkinter import ttk
from typing import Optional

# --- Google Material Design Color Palette ---
COLOR_SURFACE = "#f8f9fa"        # Google Grey 50 (App canvas background)
COLOR_CARD = "#ffffff"           # Card & Panel background (White)
COLOR_BORDER = "#dadce0"         # Google Grey 300 (Subtle borders)
COLOR_BORDER_LIGHT = "#e8eaed"   # Dividers & Hairlines (Google Grey 200)
COLOR_HOVER = "#f1f3f4"          # Google Grey 100 (Hover state)
COLOR_ACTIVE = "#e8eaed"         # Google Grey 200 (Pressed/Active state)

# Typography Colors
COLOR_TEXT_PRIMARY = "#202124"   # Google Grey 900 (High contrast headers & body)
COLOR_TEXT_SECONDARY = "#5f6368" # Google Grey 700 (Subtitles & captions)
COLOR_TEXT_MUTED = "#80868b"     # Google Grey 600 (Meta & placeholders)
COLOR_TEXT_WHITE = "#ffffff"

# Google Accent Colors
COLOR_BLUE = "#1a73e8"           # Google Blue 600
COLOR_BLUE_HOVER = "#1557b0"     # Google Blue 700
COLOR_BLUE_LIGHT = "#e8f0fe"     # Google Blue 50

COLOR_GREEN = "#1e8e3e"          # Google Green 600
COLOR_GREEN_HOVER = "#137333"    # Google Green 700
COLOR_GREEN_LIGHT = "#e6f4ea"    # Google Green 50

COLOR_YELLOW = "#f9ab00"         # Google Yellow 600
COLOR_AMBER_DARK = "#b06000"
COLOR_YELLOW_LIGHT = "#fef7e0"   # Google Yellow 50

COLOR_RED = "#d93025"            # Google Red 600
COLOR_RED_HOVER = "#b31412"      # Google Red 700
COLOR_RED_LIGHT = "#fce8e6"      # Google Red 50

COLOR_PURPLE = "#a142f4"         # Google Purple 600
COLOR_PURPLE_LIGHT = "#f3e8fd"   # Google Purple 50

# Status Color Map
STATUS_COLORS = {
    "Backlog": {"fg": COLOR_TEXT_SECONDARY, "bg": "#f1f3f4", "bar": "#80868b", "icon": "📦"},
    "To Do": {"fg": COLOR_BLUE, "bg": COLOR_BLUE_LIGHT, "bar": COLOR_BLUE, "icon": "⏳"},
    "In Progress": {"fg": COLOR_AMBER_DARK, "bg": COLOR_YELLOW_LIGHT, "bar": COLOR_YELLOW, "icon": "⚡"},
    "In Review": {"fg": COLOR_PURPLE, "bg": COLOR_PURPLE_LIGHT, "bar": COLOR_PURPLE, "icon": "🔍"},
    "Done": {"fg": COLOR_GREEN, "bg": COLOR_GREEN_LIGHT, "bar": COLOR_GREEN, "icon": "✅"},
}

# Priority Icons and Color Map
PRIORITY_CONFIG = {
    "Low": {"icon": "🟢", "fg": "#137333", "bg": "#e6f4ea"},
    "Medium": {"icon": "🔵", "fg": "#1a73e8", "bg": "#e8f0fe"},
    "High": {"icon": "🟠", "fg": "#b06000", "bg": "#fef7e0"},
    "Urgent": {"icon": "🔴", "fg": "#c5221f", "bg": "#fce8e6"},
}

# Issue Type Icons and Color Map
TYPE_CONFIG = {
    "Task": {"icon": "📋", "fg": COLOR_BLUE, "bg": COLOR_BLUE_LIGHT},
    "Bug": {"icon": "🐛", "fg": COLOR_RED, "bg": COLOR_RED_LIGHT},
    "Story": {"icon": "🚀", "fg": COLOR_GREEN, "bg": COLOR_GREEN_LIGHT},
    "Epic": {"icon": "⚡", "fg": COLOR_PURPLE, "bg": COLOR_PURPLE_LIGHT},
}

# Typography (Segoe UI with cross-platform clean fallbacks)
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 15, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_SECTION = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_CAPTION = (FONT_FAMILY, 9)
FONT_BADGE = (FONT_FAMILY, 8, "bold")


def apply_google_theme(root: tk.Tk):
    """Configures global ttk styles to replicate Google Minimalist Material Design."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=COLOR_SURFACE)

    # General Frames
    style.configure("TFrame", background=COLOR_SURFACE)
    style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")
    style.configure("White.TFrame", background=COLOR_CARD)

    # General Labels
    style.configure("TLabel", background=COLOR_SURFACE, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)
    style.configure("HeaderTitle.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT_PRIMARY, font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT_SECONDARY, font=FONT_CAPTION)

    # Primary Material Button (Google Blue with White text)
    style.configure(
        "Primary.TButton",
        background=COLOR_BLUE,
        foreground=COLOR_TEXT_WHITE,
        font=FONT_BODY_BOLD,
        borderwidth=0,
        focusthickness=0,
        focuscolor="none",
        padding=(10, 6)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_BLUE_HOVER), ("pressed", COLOR_BLUE_HOVER)],
        foreground=[("active", COLOR_TEXT_WHITE)]
    )

    # Secondary Outline Button (Subtle border, white card background)
    style.configure(
        "Secondary.TButton",
        background=COLOR_CARD,
        foreground=COLOR_TEXT_SECONDARY,
        font=FONT_BODY,
        borderwidth=1,
        relief="solid",
        padding=(10, 5)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLOR_HOVER), ("pressed", COLOR_BORDER)],
        foreground=[("active", COLOR_TEXT_PRIMARY)]
    )

    # Danger Button (Red outline for delete actions)
    style.configure(
        "Danger.TButton",
        background=COLOR_RED_LIGHT,
        foreground=COLOR_RED,
        font=FONT_BODY_BOLD,
        borderwidth=1,
        relief="solid",
        padding=(10, 5)
    )
    style.map(
        "Danger.TButton",
        background=[("active", COLOR_RED), ("pressed", COLOR_RED_HOVER)],
        foreground=[("active", COLOR_TEXT_WHITE)]
    )

    # Clean Material Scrollbar (Visible 14px thumb and track without hairline collapse)
    style.configure(
        "TScrollbar",
        background=COLOR_BORDER,
        troughcolor=COLOR_SURFACE,
        borderwidth=0,
        arrowsize=14,
        width=14,
        relief="flat"
    )
    style.map(
        "TScrollbar",
        background=[("active", COLOR_TEXT_MUTED), ("pressed", COLOR_TEXT_SECONDARY)]
    )

    # Combobox Styling
    style.configure(
        "TCombobox",
        fieldbackground=COLOR_CARD,
        background=COLOR_CARD,
        foreground=COLOR_TEXT_PRIMARY,
        arrowcolor=COLOR_TEXT_SECONDARY,
        padding=5,
        borderwidth=1,
        relief="solid"
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLOR_CARD)],
        selectbackground=[("readonly", COLOR_BLUE_LIGHT)],
        selectforeground=[("readonly", COLOR_BLUE)]
    )

    # Treeview Table (Backlog View)
    style.configure(
        "Treeview",
        background=COLOR_CARD,
        foreground=COLOR_TEXT_PRIMARY,
        fieldbackground=COLOR_CARD,
        font=FONT_BODY,
        rowheight=36,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_HOVER,
        foreground=COLOR_TEXT_SECONDARY,
        font=FONT_BODY_BOLD,
        padding=(8, 6),
        borderwidth=0
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_BLUE_LIGHT)],
        foreground=[("selected", COLOR_BLUE)]
    )


def set_window_icon(window: tk.Wm):
    """Sets the application icon for any Tk root or Toplevel window."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    ico_path = os.path.join(assets_dir, "app_icon.ico")
    png_path = os.path.join(assets_dir, "app_icon.png")

    try:
        if os.path.exists(ico_path):
            window.iconbitmap(ico_path)
        elif os.path.exists(png_path):
            img = tk.PhotoImage(file=png_path)
            window.iconphoto(True, img)
    except Exception:
        pass


def center_window(window: tk.Wm, width: int, height: int, parent: Optional[tk.Wm] = None):
    """Centers a window on screen or relative to its parent window, clamped to screen bounds."""
    window.update_idletasks()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()

    # Ensure requested dimensions fit within screen
    width = min(width, sw - 40)
    height = min(height, sh - 80)

    if parent and hasattr(parent, "winfo_ismapped") and parent.winfo_ismapped():
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + max(0, (pw - width) // 2)
        y = py + max(0, (ph - height) // 2)
    else:
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)

    # Clamp coordinates to visible screen
    x = max(10, min(x, sw - width - 10))
    y = max(10, min(y, sh - height - 40))

    window.geometry(f"{width}x{height}+{x}+{y}")


def create_material_input(parent, initial_text="", font=FONT_BODY, width=None, ipady=4):
    """
    Creates a Google Material styled Entry wrapped inside a subtle container frame
    with interactive Google Blue focus highlight.
    Returns (container_frame, entry_widget).
    """
    container = tk.Frame(
        parent,
        bg=COLOR_CARD,
        highlightbackground=COLOR_BORDER,
        highlightthickness=1,
        padx=8,
        pady=2
    )

    entry_kwargs = {
        "master": container,
        "font": font,
        "bg": COLOR_CARD,
        "fg": COLOR_TEXT_PRIMARY,
        "insertbackground": COLOR_BLUE,
        "relief": "flat",
    }
    if width is not None:
        entry_kwargs["width"] = width

    entry = tk.Entry(**entry_kwargs)
    entry.pack(fill="x", expand=True, ipady=ipady)

    if initial_text:
        entry.insert(0, initial_text)

    def _on_focus_in(event):
        container.configure(highlightbackground=COLOR_BLUE, highlightthickness=1)

    def _on_focus_out(event):
        container.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)

    entry.bind("<FocusIn>", _on_focus_in)
    entry.bind("<FocusOut>", _on_focus_out)

    return container, entry


def create_material_textarea(parent, height=4, font=FONT_BODY):
    """
    Creates a Google Material styled Text widget wrapped in a subtle container
    with interactive Google Blue focus highlight.
    Returns (container_frame, text_widget).
    """
    container = tk.Frame(
        parent,
        bg=COLOR_CARD,
        highlightbackground=COLOR_BORDER,
        highlightthickness=1,
        padx=4,
        pady=4
    )

    text = tk.Text(
        container,
        height=height,
        font=font,
        bg=COLOR_CARD,
        fg=COLOR_TEXT_PRIMARY,
        insertbackground=COLOR_BLUE,
        relief="flat",
        padx=6,
        pady=6,
        wrap="word"
    )
    text.pack(fill="both", expand=True)

    def _on_focus_in(event):
        container.configure(highlightbackground=COLOR_BLUE, highlightthickness=1)

    def _on_focus_out(event):
        container.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)

    text.bind("<FocusIn>", _on_focus_in)
    text.bind("<FocusOut>", _on_focus_out)

    return container, text
