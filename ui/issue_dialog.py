"""
Polished and modern Google Material Issue Create & Edit Modal Dialog for JiraDesk.
Features pinned bottom action bar, app icon setup, centered positioning, and focus rings.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable
from models import Issue, Project, Status
from database import Database
import theme


class IssueDialog(tk.Toplevel):
    def __init__(self, parent, db: Database, projects: List[Project], statuses: List[Status],
                 issue: Optional[Issue] = None, preselected_status_id: Optional[int] = None,
                 preselected_project_id: Optional[int] = None,
                 on_saved: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.db = db
        self.projects = projects
        self.statuses = statuses
        self.issue = issue
        self.preselected_status_id = preselected_status_id
        self.preselected_project_id = preselected_project_id
        self.on_saved = on_saved

        self.title("Edit Issue" if self.issue else "Create Issue")
        self.minsize(580, 580)
        self.configure(bg=theme.COLOR_SURFACE)

        # Apply app icon to dialog window
        theme.set_window_icon(self)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._load_data()
        self._bind_shortcuts()

        # Center dialog relative to parent window
        theme.center_window(self, 640, 700, parent)

    def _build_ui(self):
        # 1. Top Header Banner
        header = tk.Frame(self, bg=theme.COLOR_CARD, padx=24, pady=14, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        header.pack(side="top", fill="x")

        header_title = "Create New Issue" if not self.issue else f"Edit Issue: {self.issue.key}"
        lbl_title = tk.Label(header, text=header_title, font=theme.FONT_TITLE, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD)
        lbl_title.pack(side="left")

        if self.issue:
            lbl_key = tk.Label(
                header,
                text=self.issue.key,
                font=theme.FONT_BADGE,
                fg=theme.COLOR_BLUE,
                bg=theme.COLOR_BLUE_LIGHT,
                padx=8,
                pady=3
            )
            lbl_key.pack(side="right")

        # 2. Bottom Action Bar (MUST be packed BEFORE expanding canvas so it is always pinned to bottom)
        bottom_bar = tk.Frame(self, bg=theme.COLOR_CARD, padx=24, pady=14, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        bottom_bar.pack(side="bottom", fill="x")

        tk.Label(
            bottom_bar,
            text="Tip: Press Ctrl+Enter to Save, Esc to Cancel",
            font=theme.FONT_CAPTION,
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_CARD
        ).pack(side="left")

        save_btn = ttk.Button(bottom_bar, text="Save Issue", style="Primary.TButton", width=12, command=self._save_issue)
        save_btn.pack(side="right")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", style="Secondary.TButton", width=8, command=self.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))

        # 3. Middle Scrollable Form Area (expands between header and bottom_bar)
        canvas = tk.Canvas(self, bg=theme.COLOR_SURFACE, highlightthickness=0)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        self.form = tk.Frame(canvas, bg=theme.COLOR_SURFACE, padx=24, pady=16)
        canvas_window = canvas.create_window((0, 0), window=self.form, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        self.form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Mouse wheel on modal canvas
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.form.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))

        self.form.columnconfigure(0, weight=1)
        self.form.columnconfigure(1, weight=1)

        row = 0

        # Row 0: Project Selector (full width)
        tk.Label(self.form, text="Project *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.proj_combo = ttk.Combobox(self.form, state="readonly", font=theme.FONT_BODY)
        self.proj_combo["values"] = [f"{p.key} - {p.name}" for p in self.projects]
        self.proj_combo.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 2

        # Row 1: Issue Type & Priority (Symmetrical 2-column grid with balanced margins)
        tk.Label(self.form, text="Issue Type", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, sticky="w", pady=(0, 4), padx=(0, 6))
        tk.Label(self.form, text="Priority", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=1, sticky="w", pady=(0, 4), padx=(6, 0))

        self.type_combo = ttk.Combobox(self.form, state="readonly", values=["Task", "Bug", "Story", "Epic"], font=theme.FONT_BODY)
        self.type_combo.grid(row=row+1, column=0, sticky="ew", pady=(0, 12), padx=(0, 6))

        self.prio_combo = ttk.Combobox(self.form, state="readonly", values=["Low", "Medium", "High", "Urgent"], font=theme.FONT_BODY)
        self.prio_combo.grid(row=row+1, column=1, sticky="ew", pady=(0, 12), padx=(6, 0))
        row += 2

        # Row 2: Status (full width)
        tk.Label(self.form, text="Status", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.status_combo = ttk.Combobox(self.form, state="readonly", values=[s.name for s in self.statuses], font=theme.FONT_BODY)
        self.status_combo.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 2

        # Row 3: Title / Summary (full width) with Material focus ring
        tk.Label(self.form, text="Summary / Title *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        title_box, self.title_entry = theme.create_material_input(self.form, font=theme.FONT_BODY, ipady=4)
        title_box.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 2

        # Row 4: Description with Material focus ring
        tk.Label(self.form, text="Description", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        desc_box, self.desc_text = theme.create_material_textarea(self.form, height=4, font=theme.FONT_BODY)
        desc_box.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        row += 2

        # Time Tracking Section
        worklog_box = tk.LabelFrame(
            self.form,
            text="  Time Tracking & Worklogs  ",
            font=theme.FONT_SECTION,
            fg=theme.COLOR_TEXT_PRIMARY,
            bg=theme.COLOR_SURFACE,
            padx=14,
            pady=10
        )
        worklog_box.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        row += 1

        input_frame = tk.Frame(worklog_box, bg=theme.COLOR_SURFACE)
        input_frame.pack(fill="x", pady=(0, 8))

        tk.Label(input_frame, text="Time Spent:", font=theme.FONT_BODY, bg=theme.COLOR_SURFACE).pack(side="left", padx=(0, 6), pady=2)
        time_entry_box, self.time_val_entry = theme.create_material_input(input_frame, initial_text="30", width=6, ipady=3)
        time_entry_box.pack(side="left", pady=2)

        self.time_unit_combo = ttk.Combobox(input_frame, state="readonly", values=["Minutes", "Hours"], width=8, font=theme.FONT_BODY)
        self.time_unit_combo.current(0)
        self.time_unit_combo.pack(side="left", padx=(6, 12), pady=2)

        tk.Label(input_frame, text="Notes:", font=theme.FONT_BODY, bg=theme.COLOR_SURFACE).pack(side="left", padx=(0, 6), pady=2)
        notes_box, self.worklog_notes_entry = theme.create_material_input(input_frame, ipady=3)
        notes_box.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=2)

        if self.issue:
            log_btn = tk.Button(
                input_frame,
                text="+ Log Time",
                font=theme.FONT_CAPTION,
                bg=theme.COLOR_BLUE_LIGHT,
                fg=theme.COLOR_BLUE,
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3,
                command=self._add_worklog
            )
            log_btn.pack(side="right", pady=2)
            log_btn.bind("<Enter>", lambda e, b=log_btn: b.configure(bg=theme.COLOR_BLUE, fg=theme.COLOR_TEXT_WHITE))
            log_btn.bind("<Leave>", lambda e, b=log_btn: b.configure(bg=theme.COLOR_BLUE_LIGHT, fg=theme.COLOR_BLUE))

            # Modern Worklogs List container
            list_container = tk.Frame(worklog_box, bg=theme.COLOR_CARD, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
            list_container.pack(fill="x", pady=(4, 0))

            self.worklogs_listbox = tk.Listbox(
                list_container,
                height=3,
                font=theme.FONT_CAPTION,
                bg=theme.COLOR_CARD,
                fg=theme.COLOR_TEXT_SECONDARY,
                selectbackground=theme.COLOR_BLUE_LIGHT,
                selectforeground=theme.COLOR_BLUE,
                relief="flat",
                bd=0,
                highlightthickness=0
            )
            self.worklogs_listbox.pack(fill="x", padx=6, pady=4)
            self._refresh_worklogs()
        else:
            tk.Label(
                worklog_box,
                text="ℹ️  Time entered above will be logged upon saving this new issue.",
                font=theme.FONT_CAPTION,
                fg=theme.COLOR_TEXT_MUTED,
                bg=theme.COLOR_SURFACE
            ).pack(anchor="w", pady=(2, 0))

        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="top", fill="both", expand=True)

    def _bind_shortcuts(self):
        self.bind("<Control-Return>", lambda e: self._save_issue())
        self.bind("<Escape>", lambda e: self.destroy())

    def _load_data(self):
        if self.issue:
            for idx, p in enumerate(self.projects):
                if p.id == self.issue.project_id:
                    self.proj_combo.current(idx)
                    break
            self.type_combo.set(self.issue.issue_type)
            self.status_combo.set(self.issue.status_name)
            self.prio_combo.set(self.issue.priority)
            self.title_entry.insert(0, self.issue.title)
            self.desc_text.insert("1.0", self.issue.description)
        else:
            if self.projects:
                proj_idx = 0
                if self.preselected_project_id:
                    for idx, p in enumerate(self.projects):
                        if p.id == self.preselected_project_id:
                            proj_idx = idx
                            break
                self.proj_combo.current(proj_idx)

            self.type_combo.current(0)  # Task
            self.prio_combo.current(1)  # Medium

            if self.preselected_status_id:
                for s in self.statuses:
                    if s.id == self.preselected_status_id:
                        self.status_combo.set(s.name)
                        break
            else:
                self.status_combo.current(0)

        # Set initial focus on title
        self.after(50, lambda: self.title_entry.focus_set())

    def _refresh_worklogs(self):
        if not self.issue:
            return
        self.worklogs_listbox.delete(0, tk.END)
        logs = self.db.get_worklogs(self.issue.id)
        if not logs:
            self.worklogs_listbox.insert(tk.END, "  No work logged yet.")
        else:
            for l in logs:
                note_str = f" — {l.notes}" if l.notes else ""
                self.worklogs_listbox.insert(
                    tk.END,
                    f"  ⏱ {l.formatted_time} [{l.logged_at[:16]}]{note_str}"
                )

    def _add_worklog(self):
        if not self.issue:
            return
        val_str = self.time_val_entry.get().strip()
        try:
            val = float(val_str)
            if val <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a positive numeric time value.", parent=self)
            return

        unit = self.time_unit_combo.get()
        minutes = int(val * 60) if unit == "Hours" else int(val)
        notes = self.worklog_notes_entry.get().strip()

        self.db.add_worklog(self.issue.id, minutes, notes)
        self.worklog_notes_entry.delete(0, tk.END)
        self._refresh_worklogs()
        if self.on_saved:
            self.on_saved()

    def _save_issue(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please provide an issue summary/title.", parent=self)
            self.title_entry.focus_set()
            return

        selected_proj_idx = self.proj_combo.current()
        if selected_proj_idx < 0:
            combo_val = self.proj_combo.get().strip()
            matched_proj = None
            for p in self.projects:
                if combo_val.startswith(p.key):
                    matched_proj = p
                    break
            if not matched_proj and self.projects:
                matched_proj = self.projects[0]
            if not matched_proj:
                messagebox.showwarning("Missing Project", "Please select a valid project.", parent=self)
                return
            project_id = matched_proj.id
        else:
            project_id = self.projects[selected_proj_idx].id

        issue_type = self.type_combo.get() or "Task"
        priority = self.prio_combo.get() or "Medium"

        status_name = self.status_combo.get()
        status_id = self.statuses[0].id if self.statuses else 1
        for s in self.statuses:
            if s.name == status_name:
                status_id = s.id
                break

        description = self.desc_text.get("1.0", tk.END).strip()

        if self.issue:
            self.db.update_issue(
                issue_id=self.issue.id,
                title=title,
                description=description,
                issue_type=issue_type,
                priority=priority,
                status_id=status_id
            )
        else:
            new_id = self.db.create_issue(
                project_id=project_id,
                title=title,
                description=description,
                issue_type=issue_type,
                priority=priority,
                status_id=status_id
            )
            # Check if user entered initial worklog time
            val_str = self.time_val_entry.get().strip()
            try:
                val = float(val_str)
                if val > 0:
                    unit = self.time_unit_combo.get()
                    minutes = int(val * 60) if unit == "Hours" else int(val)
                    notes = self.worklog_notes_entry.get().strip()
                    self.db.add_worklog(new_id, minutes, notes)
            except Exception:
                pass

        if self.on_saved:
            self.on_saved()
        self.destroy()
