"""
Google Minimalist Material Design Theme for JiraDesk.
"""
import tkinter as tk
from tkinter import ttk

# --- Google Material Design Color Palette ---
COLOR_SURFACE = "#f8f9fa"        # Google Grey 50 (App background)
COLOR_CARD = "#ffffff"           # Card & Panel background
COLOR_BORDER = "#dadce0"         # Google Grey 300 (Subtle borders)
COLOR_BORDER_LIGHT = "#e8eaed"   # Dividers
COLOR_HOVER = "#f1f3f4"          # Google Grey 100
COLOR_ACTIVE = "#e8eaed"         # Google Grey 200

# Typography Colors
COLOR_TEXT_PRIMARY = "#202124"   # Google Grey 900
COLOR_TEXT_SECONDARY = "#5f6368" # Google Grey 700
COLOR_TEXT_MUTED = "#80868b"     # Google Grey 600
COLOR_TEXT_WHITE = "#ffffff"

# Google Accent Colors
COLOR_BLUE = "#1a73e8"           # Google Blue 600
COLOR_BLUE_HOVER = "#1557b0"     # Google Blue 700
COLOR_BLUE_LIGHT = "#e8f0fe"     # Google Blue 50

COLOR_GREEN = "#1e8e3e"          # Google Green 600
COLOR_GREEN_LIGHT = "#e6f4ea"    # Google Green 50

COLOR_YELLOW = "#f9ab00"         # Google Yellow 600
COLOR_AMBER_DARK = "#b06000"
COLOR_YELLOW_LIGHT = "#fef7e0"   # Google Yellow 50

COLOR_RED = "#d93025"            # Google Red 600
COLOR_RED_LIGHT = "#fce8e6"      # Google Red 50

COLOR_PURPLE = "#a142f4"         # Google Purple 600
COLOR_PURPLE_LIGHT = "#f3e8fd"   # Google Purple 50

# Status Color Map
STATUS_COLORS = {
    "Backlog": {"fg": COLOR_TEXT_SECONDARY, "bg": "#f1f3f4", "bar": "#80868b"},
    "To Do": {"fg": COLOR_BLUE, "bg": COLOR_BLUE_LIGHT, "bar": COLOR_BLUE},
    "In Progress": {"fg": COLOR_AMBER_DARK, "bg": COLOR_YELLOW_LIGHT, "bar": COLOR_YELLOW},
    "In Review": {"fg": COLOR_PURPLE, "bg": COLOR_PURPLE_LIGHT, "bar": COLOR_PURPLE},
    "Done": {"fg": COLOR_GREEN, "bg": COLOR_GREEN_LIGHT, "bar": COLOR_GREEN},
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

# Typography
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
        padding=(14, 7)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_BLUE_HOVER), ("pressed", COLOR_BLUE_HOVER)],
        foreground=[("active", COLOR_TEXT_WHITE)]
    )

    # Secondary Outline Button
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

    # Clean Material Entry Field
    style.configure(
        "Google.TEntry",
        fieldbackground=COLOR_CARD,
        foreground=COLOR_TEXT_PRIMARY,
        bordercolor=COLOR_BORDER,
        lightcolor=COLOR_BLUE,
        darkcolor=COLOR_BORDER,
        padding=6,
        relief="flat"
    )

    # Combobox
    style.configure(
        "Google.TCombobox",
        fieldbackground=COLOR_CARD,
        background=COLOR_CARD,
        foreground=COLOR_TEXT_PRIMARY,
        arrowcolor=COLOR_TEXT_SECONDARY,
        padding=5
    )

    # Treeview Table (Backlog View)
    style.configure(
        "Treeview",
        background=COLOR_CARD,
        foreground=COLOR_TEXT_PRIMARY,
        fieldbackground=COLOR_CARD,
        font=FONT_BODY,
        rowheight=34,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_HOVER,
        foreground=COLOR_TEXT_SECONDARY,
        font=FONT_BODY_BOLD,
        padding=6,
        borderwidth=0
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_BLUE_LIGHT)],
        foreground=[("selected", COLOR_BLUE)]
    )
