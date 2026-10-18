"""
Polished and modern Google Material Project Creation Modal Dialog for JiraDesk.
Features pinned bottom action bar, app icon setup, centered positioning, and focus rings.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from database import Database
import theme


class ProjectDialog(tk.Toplevel):
    def __init__(self, parent, db: Database, on_created: Optional[Callable[[int], None]] = None):
        super().__init__(parent)
        self.db = db
        self.on_created = on_created

        self.title("Create New Project")
        self.resizable(False, False)
        self.configure(bg=theme.COLOR_SURFACE)

        # Apply app icon to dialog window
        theme.set_window_icon(self)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._bind_shortcuts()

        # Center dialog relative to parent window
        theme.center_window(self, 480, 390, parent)

    def _build_ui(self):
        # 1. Top Header Banner
        header = tk.Frame(self, bg=theme.COLOR_CARD, padx=24, pady=16, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        header.pack(side="top", fill="x")

        lbl_title = tk.Label(header, text="Create Workspace Project", font=theme.FONT_TITLE, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD)
        lbl_title.pack(side="left")

        # 2. Bottom Action Bar (MUST be packed BEFORE expanding form to prevent being pushed off-screen)
        bottom_bar = tk.Frame(self, bg=theme.COLOR_CARD, padx=24, pady=14, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        bottom_bar.pack(side="bottom", fill="x")

        tk.Label(
            bottom_bar,
            text="Tip: Press Enter to Create, Esc to Cancel",
            font=theme.FONT_CAPTION,
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_CARD
        ).pack(side="left")

        create_btn = ttk.Button(bottom_bar, text="Create Project", style="Primary.TButton", width=14, command=self._create_project)
        create_btn.pack(side="right")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", style="Secondary.TButton", width=8, command=self.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))

        # 3. Middle Form Area (expands between header and bottom_bar)
        form = tk.Frame(self, bg=theme.COLOR_SURFACE, padx=24, pady=16)
        form.pack(side="top", fill="both", expand=True)

        # Project Key
        tk.Label(form, text="Project Key (e.g., DEV, APP, LIFE) *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_SURFACE).pack(anchor="w", pady=(0, 2))
        tk.Label(form, text="2–10 uppercase letters used as prefix (e.g., DEV-101)", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_MUTED, bg=theme.COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        key_box, self.key_entry = theme.create_material_input(form, ipady=4)
        key_box.pack(fill="x", pady=(0, 12))
        self.key_entry.bind("<KeyRelease>", self._on_key_release)

        # Project Name
        tk.Label(form, text="Project Name *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        name_box, self.name_entry = theme.create_material_input(form, ipady=4)
        name_box.pack(fill="x", pady=(0, 12))

        # Description
        tk.Label(form, text="Description (Optional)", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        desc_box, self.desc_entry = theme.create_material_input(form, ipady=4)
        desc_box.pack(fill="x", pady=(0, 8))

        self.after(50, lambda: self.key_entry.focus_set())

    def _on_key_release(self, event=None):
        """Auto-formats key to uppercase."""
        pos = self.key_entry.index(tk.INSERT)
        val = self.key_entry.get().upper()
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, val)
        self.key_entry.icursor(pos)

    def _bind_shortcuts(self):
        self.bind("<Return>", lambda e: self._create_project())
        self.bind("<Escape>", lambda e: self.destroy())

    def _create_project(self):
        key = self.key_entry.get().strip().upper()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not key or not name:
            messagebox.showwarning("Missing Fields", "Please provide both a project key and project name.", parent=self)
            return

        if len(key) < 2 or len(key) > 10 or not key.isalnum():
            messagebox.showwarning("Invalid Key", "Key must be 2 to 10 alphanumeric characters (e.g. 'DEV', 'APP').", parent=self)
            self.key_entry.focus_set()
            return

        # Check for duplicate key
        existing = self.db.get_project_by_key(key)
        if existing:
            messagebox.showwarning("Duplicate Key", f"Project key '{key}' already exists. Please choose a different key.", parent=self)
            self.key_entry.focus_set()
            return

        try:
            proj_id = self.db.create_project(key, name, desc)
            if self.on_created:
                self.on_created(proj_id)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}", parent=self)
