"""
Main Application Container & Controller for JiraDesk.
Includes full Backup, Restore, Reset (Start Fresh / Samples), Export, and responsive views.
"""
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from database import Database
from models import Project, Status, Issue
from ui.kanban_view import KanbanView
from ui.table_view import TableView
from ui.issue_dialog import IssueDialog
from ui.project_dialog import ProjectDialog
import theme


class JiraDeskApp(tk.Tk):
    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.title("JiraDesk — Personal Workflow Tracker")
        self.geometry("1280x820")
        self.minsize(980, 640)

        theme.apply_google_theme(self)

        self.db = Database(db_path)
        self.statuses: List[Status] = self.db.get_statuses()
        self.projects: List[Project] = self.db.get_projects()

        self.current_project_id: Optional[int] = None
        self.current_view_mode = "kanban"
        self.search_term = ""

        self._setup_icon()
        self._build_header()
        self._build_stats_bar()
        self._build_content_area()
        self._build_status_bar()
        self._bind_global_shortcuts()

        self.refresh_all()

    def _setup_icon(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        ico_path = os.path.join(assets_dir, "app_icon.ico")
        png_path = os.path.join(assets_dir, "app_icon.png")

        try:
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, img)
        except Exception:
            pass

    def _build_header(self):
        header = tk.Frame(self, bg=theme.COLOR_CARD, padx=20, pady=10, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x")

        # Left: App Brand & Subtitle
        left_box = tk.Frame(header, bg=theme.COLOR_CARD)
        left_box.pack(side="left")

        title_box = tk.Frame(left_box, bg=theme.COLOR_CARD)
        title_box.pack(side="left")

        lbl_brand = tk.Label(title_box, text="JiraDesk", font=theme.FONT_TITLE, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD)
        lbl_brand.pack(anchor="w")

        lbl_sub = tk.Label(title_box, text="Personal Workflow Tracker", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_MUTED, bg=theme.COLOR_CARD)
        lbl_sub.pack(anchor="w")

        # Controls Container on Right
        controls_box = tk.Frame(header, bg=theme.COLOR_CARD)
        controls_box.pack(side="right")

        # 1. Project Selector Group
        proj_group = tk.Frame(controls_box, bg=theme.COLOR_CARD)
        proj_group.pack(side="left", padx=(0, 10))

        tk.Label(proj_group, text="Project:", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_CARD).pack(side="left", padx=(0, 6))
        self.proj_combo = ttk.Combobox(proj_group, state="readonly", width=16, font=theme.FONT_BODY)
        self.proj_combo.pack(side="left", padx=(0, 6))
        self.proj_combo.bind("<<ComboboxSelected>>", self._on_project_changed)

        new_proj_btn = ttk.Button(proj_group, text="+ Project", style="Secondary.TButton", command=self._open_new_project_dialog)
        new_proj_btn.pack(side="left")

        # Divider between project and search
        tk.Frame(controls_box, bg=theme.COLOR_BORDER, width=1, height=22).pack(side="left", padx=(0, 10))

        # 2. Google Material Search Bar with Dynamic Focus Highlight
        self.search_frame = tk.Frame(
            controls_box,
            bg=theme.COLOR_HOVER,
            highlightbackground=theme.COLOR_BORDER,
            highlightthickness=1,
            padx=8,
            pady=3
        )
        self.search_frame.pack(side="left", padx=(0, 10))

        self.lbl_search_icon = tk.Label(self.search_frame, text="🔍", font=theme.FONT_CAPTION, bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_MUTED)
        self.lbl_search_icon.pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(
            self.search_frame,
            font=theme.FONT_BODY,
            bg=theme.COLOR_HOVER,
            fg=theme.COLOR_TEXT_PRIMARY,
            insertbackground=theme.COLOR_BLUE,
            relief="flat",
            width=18
        )
        self.search_entry.pack(side="left", ipady=2)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        self.btn_clear_search = tk.Label(
            self.search_frame,
            text="✕",
            font=theme.FONT_BADGE,
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_HOVER,
            cursor="hand2",
            padx=2
        )
        self.btn_clear_search.pack(side="left", padx=(2, 0))
        self.btn_clear_search.bind("<Button-1>", self._clear_search)
        self.btn_clear_search.bind("<Enter>", lambda e: self.btn_clear_search.configure(fg=theme.COLOR_TEXT_PRIMARY))
        self.btn_clear_search.bind("<Leave>", lambda e: self.btn_clear_search.configure(fg=theme.COLOR_TEXT_MUTED))
        self.btn_clear_search.pack_forget()

        # 3. Modern Segmented View Switcher Pill (Board vs List)
        view_toggle_frame = tk.Frame(controls_box, bg=theme.COLOR_HOVER, padx=2, pady=2)
        view_toggle_frame.pack(side="left", padx=(0, 12))

        self.btn_kanban = tk.Label(
            view_toggle_frame,
            text="⊞ Board",
            font=theme.FONT_CAPTION,
            bg=theme.COLOR_CARD,
            fg=theme.COLOR_BLUE,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_kanban.pack(side="left")
        self.btn_kanban.bind("<Button-1>", lambda e: self._set_view_mode("kanban"))

        self.btn_table = tk.Label(
            view_toggle_frame,
            text="☰ List",
            font=theme.FONT_CAPTION,
            bg=theme.COLOR_HOVER,
            fg=theme.COLOR_TEXT_SECONDARY,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_table.pack(side="left")
        self.btn_table.bind("<Button-1>", lambda e: self._set_view_mode("table"))

        # 4. Action Buttons
        create_btn = ttk.Button(controls_box, text="+ Create Issue", style="Primary.TButton", command=self._open_new_issue_dialog)
        create_btn.pack(side="left", padx=(0, 8))

        self.btn_data_menu = ttk.Button(controls_box, text="⚙ Data & Backup ▾", style="Secondary.TButton", command=self._show_data_menu)
        self.btn_data_menu.pack(side="left")

    def _on_search_focus_in(self, event=None):
        self.search_frame.configure(bg=theme.COLOR_CARD, highlightbackground=theme.COLOR_BLUE, highlightthickness=1)
        self.lbl_search_icon.configure(bg=theme.COLOR_CARD, fg=theme.COLOR_BLUE)
        self.search_entry.configure(bg=theme.COLOR_CARD)
        self.btn_clear_search.configure(bg=theme.COLOR_CARD)

    def _on_search_focus_out(self, event=None):
        if not self.search_term:
            self.search_frame.configure(bg=theme.COLOR_HOVER, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
            self.lbl_search_icon.configure(bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_MUTED)
            self.search_entry.configure(bg=theme.COLOR_HOVER)
            self.btn_clear_search.configure(bg=theme.COLOR_HOVER)
        else:
            self.search_frame.configure(highlightbackground=theme.COLOR_BORDER, highlightthickness=1)

    def _create_chip(self, parent, text, icon, fg_color, bg_color):
        """Creates a modern Google Material chip widget."""
        chip_frame = tk.Frame(
            parent,
            bg=bg_color,
            highlightbackground=theme.COLOR_BORDER,
            highlightthickness=1,
            padx=8,
            pady=3
        )
        chip_frame.pack(side="left", padx=(0, 8))

        icon_lbl = tk.Label(chip_frame, text=icon, font=theme.FONT_CAPTION, fg=fg_color, bg=bg_color)
        icon_lbl.pack(side="left", padx=(0, 4))

        val_lbl = tk.Label(chip_frame, text=text, font=theme.FONT_BADGE, fg=fg_color, bg=bg_color)
        val_lbl.pack(side="left")

        return chip_frame, val_lbl

    def _build_stats_bar(self):
        self.stats_bar_outer = tk.Frame(self, bg=theme.COLOR_SURFACE)
        self.stats_bar_outer.pack(fill="x")

        self.stats_bar = tk.Frame(self.stats_bar_outer, bg=theme.COLOR_SURFACE, padx=20, pady=8)
        self.stats_bar.pack(fill="x")

        # Clean Google Material metric chips
        _, self.chip_total = self._create_chip(
            self.stats_bar, "Total: 0", "📊", theme.COLOR_TEXT_PRIMARY, theme.COLOR_CARD
        )
        _, self.chip_todo = self._create_chip(
            self.stats_bar, "To Do: 0", "⏳", theme.COLOR_BLUE, theme.COLOR_BLUE_LIGHT
        )
        _, self.chip_in_progress = self._create_chip(
            self.stats_bar, "In Progress: 0", "⚡", theme.COLOR_AMBER_DARK, theme.COLOR_YELLOW_LIGHT
        )
        _, self.chip_done = self._create_chip(
            self.stats_bar, "Done: 0", "✅", theme.COLOR_GREEN, theme.COLOR_GREEN_LIGHT
        )
        _, self.chip_time = self._create_chip(
            self.stats_bar, "0m Logged", "⏱", theme.COLOR_TEXT_SECONDARY, theme.COLOR_HOVER
        )

        # Subtle bottom divider line
        divider = tk.Frame(self.stats_bar_outer, bg=theme.COLOR_BORDER_LIGHT, height=1)
        divider.pack(fill="x")

    def _build_content_area(self):
        self.content_frame = tk.Frame(self, bg=theme.COLOR_SURFACE)
        self.content_frame.pack(fill="both", expand=True)

        self.kanban_view = KanbanView(
            self.content_frame,
            statuses=self.statuses,
            on_open_issue=self._on_open_issue,
            on_status_change=self._on_status_change,
            on_delete_issue=self._on_delete_issue,
            on_log_time=self._on_open_issue,
            on_create_issue_with_status=self._open_new_issue_with_status
        )

        self.table_view = TableView(
            self.content_frame,
            statuses=self.statuses,
            on_open_issue=self._on_open_issue,
            on_status_change=self._on_status_change,
            on_delete_issue=self._on_delete_issue,
            on_log_time=self._on_open_issue
        )

        self.kanban_view.pack(fill="both", expand=True)

    def _build_status_bar(self):
        status_bar = tk.Frame(self, bg=theme.COLOR_CARD, padx=16, pady=6, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        status_bar.pack(fill="x", side="bottom")

        # Left status indicator
        left_status = tk.Frame(status_bar, bg=theme.COLOR_CARD)
        left_status.pack(side="left")

        dot = tk.Label(left_status, text="●", font=(theme.FONT_FAMILY, 9), fg=theme.COLOR_GREEN, bg=theme.COLOR_CARD)
        dot.pack(side="left", padx=(0, 4))

        self.lbl_status_msg = tk.Label(left_status, text="Ready", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_CARD)
        self.lbl_status_msg.pack(side="left")

        # Right status indicator
        right_status = tk.Frame(status_bar, bg=theme.COLOR_CARD)
        right_status.pack(side="right")

        lbl_shortcuts = tk.Label(right_status, text="Ctrl+N: New • Ctrl+F: Search • F5: Refresh", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_MUTED, bg=theme.COLOR_CARD)
        lbl_shortcuts.pack(side="left", padx=(0, 16))

        db_name = os.path.basename(self.db.db_path)
        lbl_db = tk.Label(right_status, text=f"🗄️ SQLite: {db_name}", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_MUTED, bg=theme.COLOR_CARD)
        lbl_db.pack(side="left")

    def _bind_global_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._open_new_issue_dialog())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<F5>", lambda e: self.refresh_all())

    # --- Data & Backup Menu Operations ---
    def _show_data_menu(self):
        menu = tk.Menu(self, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
        
        menu.add_command(label="📁  Backup Database...", command=self._action_backup_database)
        menu.add_command(label="📥  Restore Database from Backup...", command=self._action_restore_database)
        menu.add_command(label="📤  Export All Data (JSON)...", command=self._action_export_json)
        menu.add_separator()
        menu.add_command(label="🔄  Reset with Sample Data...", command=self._action_reset_samples)
        menu.add_command(label="⚠️  Start Fresh (Clear All Data)...", command=self._action_start_fresh)
        menu.add_separator()

        if self.current_project_id:
            curr_proj = self.db.get_project_by_id(self.current_project_id)
            if curr_proj:
                menu.add_command(label=f"🗑️  Delete Project '{curr_proj.key}'...", command=lambda: self._action_delete_project(curr_proj))

        try:
            x = self.btn_data_menu.winfo_rootx()
            y = self.btn_data_menu.winfo_rooty() + self.btn_data_menu.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _action_backup_database(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"jira_backup_{timestamp}.db"
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Database Backup",
            initialfile=default_name,
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.db.backup_database(file_path)
                messagebox.showinfo("Backup Successful", f"Database successfully backed up to:\n{file_path}", parent=self)
                self.lbl_status_msg.configure(text=f"Backup saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Backup Failed", f"Could not create backup: {e}", parent=self)

    def _action_restore_database(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select JiraDesk Backup Database to Restore",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Restoring will overwrite current workspace data with the contents of this backup.\n\nAre you sure you want to proceed?",
                icon="warning",
                parent=self
            )
            if confirm:
                try:
                    self.db.restore_database(file_path)
                    self.current_project_id = None
                    self.refresh_all()
                    messagebox.showinfo("Restore Complete", "Workspace data has been successfully restored from backup!", parent=self)
                except Exception as e:
                    messagebox.showerror("Restore Failed", f"Could not restore database:\n{e}", parent=self)

    def _action_export_json(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"jira_export_{timestamp}.json"
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Workspace Data as JSON",
            initialfile=default_name,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.db.export_data_json(file_path)
                messagebox.showinfo("Export Successful", f"Workspace data exported to:\n{file_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not export data: {e}", parent=self)

    def _action_reset_samples(self):
        confirm = messagebox.askyesno(
            "Reset with Sample Data",
            "This will reset all current issues and projects and restore the default sample board.\n\nDo you want to proceed?",
            icon="question",
            parent=self
        )
        if confirm:
            self.db.reset_database(seed_samples=True)
            self.current_project_id = None
            self.refresh_all()
            messagebox.showinfo("Reset Completed", "Workspace has been reset with sample tasks and projects.", parent=self)

    def _action_start_fresh(self):
        ask_backup = messagebox.askyesnocancel(
            "Start Fresh (Clear All Data)",
            "Would you like to backup your current database before starting fresh?\n\n• Yes: Backup first, then start fresh\n• No: Start fresh immediately without backup\n• Cancel: Abort",
            icon="warning",
            parent=self
        )
        if ask_backup is None:
            return

        if ask_backup is True:
            self._action_backup_database()

        self.db.reset_database(seed_samples=False)
        self.current_project_id = None
        self.refresh_all()
        messagebox.showinfo("Fresh Workspace Ready", "All prior data cleared. You have a fresh, blank workspace ready for your personal tasks!", parent=self)

    def _action_delete_project(self, project: Project):
        if len(self.projects) <= 1:
            messagebox.showwarning("Cannot Delete", "You cannot delete the only remaining workspace project. Create a new project first.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirm Project Deletion",
            f"Are you sure you want to permanently delete project '{project.key} - {project.name}'?\n\nAll issues and logged time inside this project will be deleted.",
            icon="warning",
            parent=self
        )
        if confirm:
            self.db.delete_project(project.id)
            self.current_project_id = None
            self.refresh_all()

    # --- View Actions & Data Binding ---
    def refresh_all(self):
        self.projects = self.db.get_projects()
        self._update_project_dropdown()

        issues = self.db.get_issues(
            project_id=self.current_project_id,
            search_query=self.search_term
        )

        self.kanban_view.populate(issues)
        self.table_view.populate(issues)

        stats = self.db.get_statistics(self.current_project_id)
        self.chip_total.configure(text=f"Total: {stats['total']}")
        
        # Calculate to do count
        todo_count = 0
        for i in issues:
            if i.status_id == 2 or i.status_name == "To Do":
                todo_count += 1
        self.chip_todo.configure(text=f"To Do: {todo_count}")
        self.chip_in_progress.configure(text=f"In Progress: {stats['in_progress']}")
        self.chip_done.configure(text=f"Done: {stats['done']}")
        self.chip_time.configure(text=f"{stats['formatted_time']} Logged")

        curr_proj_name = "All Projects"
        if self.current_project_id:
            p = self.db.get_project_by_id(self.current_project_id)
            if p:
                curr_proj_name = f"{p.key}"

        if self.search_term:
            self.lbl_status_msg.configure(text=f"Filtering '{self.search_term}': {len(issues)} matching issue(s) • {curr_proj_name}")
        else:
            self.lbl_status_msg.configure(text=f"Loaded {len(issues)} issue(s) • {curr_proj_name}")

    def _update_project_dropdown(self):
        values = ["All Projects"] + [f"{p.key} - {p.name}" for p in self.projects]
        self.proj_combo["values"] = values
        if self.current_project_id is None:
            self.proj_combo.current(0)
        else:
            found = False
            for idx, p in enumerate(self.projects):
                if p.id == self.current_project_id:
                    self.proj_combo.current(idx + 1)
                    found = True
                    break
            if not found:
                self.proj_combo.current(0)
                self.current_project_id = None

    def _on_project_changed(self, event=None):
        sel_idx = self.proj_combo.current()
        if sel_idx <= 0:
            self.current_project_id = None
        else:
            self.current_project_id = self.projects[sel_idx - 1].id
        self.refresh_all()

    def _on_search_key(self, event=None):
        self.search_term = self.search_entry.get().strip()
        if self.search_term:
            self.btn_clear_search.pack(side="left", padx=(2, 0))
        else:
            self.btn_clear_search.pack_forget()
        self.refresh_all()

    def _clear_search(self, event=None):
        self.search_entry.delete(0, tk.END)
        self.search_term = ""
        self.btn_clear_search.pack_forget()
        self._on_search_focus_out()
        self.refresh_all()

    def _set_view_mode(self, mode: str):
        if mode == self.current_view_mode:
            return
        self.current_view_mode = mode
        if mode == "kanban":
            self.table_view.pack_forget()
            self.kanban_view.pack(fill="both", expand=True)
            self.btn_kanban.configure(bg=theme.COLOR_CARD, fg=theme.COLOR_BLUE)
            self.btn_table.configure(bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_SECONDARY)
        else:
            self.kanban_view.pack_forget()
            self.table_view.pack(fill="both", expand=True)
            self.btn_table.configure(bg=theme.COLOR_CARD, fg=theme.COLOR_BLUE)
            self.btn_kanban.configure(bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_SECONDARY)

    def _open_new_issue_dialog(self):
        IssueDialog(
            parent=self,
            db=self.db,
            projects=self.projects,
            statuses=self.statuses,
            preselected_project_id=self.current_project_id,
            on_saved=self.refresh_all
        )

    def _open_new_issue_with_status(self, status_id: int):
        IssueDialog(
            parent=self,
            db=self.db,
            projects=self.projects,
            statuses=self.statuses,
            preselected_status_id=status_id,
            preselected_project_id=self.current_project_id,
            on_saved=self.refresh_all
        )

    def _on_open_issue(self, issue_id: int):
        issue = self.db.get_issue_by_id(issue_id)
        if issue:
            IssueDialog(
                parent=self,
                db=self.db,
                projects=self.projects,
                statuses=self.statuses,
                issue=issue,
                on_saved=self.refresh_all
            )

    def _on_status_change(self, issue_id: int, new_status_id: int):
        self.db.update_issue_status(issue_id, new_status_id)
        self.refresh_all()

    def _on_delete_issue(self, issue_id: int):
        issue = self.db.get_issue_by_id(issue_id)
        if not issue:
            return
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete {issue.key}: '{issue.title}'?\n\nThis action cannot be undone.",
            icon="warning",
            parent=self
        )
        if confirm:
            self.db.delete_issue(issue_id)
            self.refresh_all()

    def _open_new_project_dialog(self):
        def on_created(proj_id):
            self.current_project_id = proj_id
            self.refresh_all()

        ProjectDialog(parent=self, db=self.db, on_created=on_created)
