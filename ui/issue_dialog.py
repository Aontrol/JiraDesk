"""
Polished and dumb-proof Issue Create & Edit Modal Dialog for JiraDesk.
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
        self.geometry("640x740")
        self.minsize(560, 600)
        self.configure(bg=theme.COLOR_SURFACE)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._load_data()
        self._bind_shortcuts()

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=theme.COLOR_CARD, padx=20, pady=16, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x")

        header_title = "Create New Issue" if not self.issue else f"{self.issue.key}: Edit Issue"
        lbl_title = tk.Label(header, text=header_title, font=theme.FONT_TITLE, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD)
        lbl_title.pack(side="left")

        # Scrollable form container
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

        row = 0

        # Project Selector
        tk.Label(self.form, text="Project *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, sticky="w", pady=(0, 4))
        self.proj_combo = ttk.Combobox(self.form, state="readonly", font=theme.FONT_BODY)
        self.proj_combo["values"] = [f"{p.key} - {p.name}" for p in self.projects]
        self.proj_combo.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 2

        # Issue Type & Status (Two columns)
        tk.Label(self.form, text="Issue Type", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, sticky="w", pady=(0, 4))
        tk.Label(self.form, text="Status", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=1, sticky="w", pady=(0, 4), padx=(12, 0))
        
        self.type_combo = ttk.Combobox(self.form, state="readonly", values=["Task", "Bug", "Story", "Epic"], font=theme.FONT_BODY)
        self.type_combo.grid(row=row+1, column=0, sticky="ew", pady=(0, 12))

        self.status_combo = ttk.Combobox(self.form, state="readonly", values=[s.name for s in self.statuses], font=theme.FONT_BODY)
        self.status_combo.grid(row=row+1, column=1, sticky="ew", pady=(0, 12), padx=(12, 0))
        row += 2

        # Priority
        tk.Label(self.form, text="Priority", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, sticky="w", pady=(0, 4))
        self.prio_combo = ttk.Combobox(self.form, state="readonly", values=["Low", "Medium", "High", "Urgent"], font=theme.FONT_BODY)
        self.prio_combo.grid(row=row+1, column=0, sticky="ew", pady=(0, 12))
        row += 2

        # Title
        tk.Label(self.form, text="Summary / Title *", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.title_entry = tk.Entry(self.form, font=theme.FONT_BODY, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, relief="solid", bd=1)
        self.title_entry.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 14), ipady=5)
        row += 2

        # Description
        tk.Label(self.form, text="Description", font=theme.FONT_BODY_BOLD, fg=theme.COLOR_TEXT_SECONDARY, bg=theme.COLOR_SURFACE).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        desc_container = tk.Frame(self.form, bg=theme.COLOR_CARD, bd=1, relief="solid")
        desc_container.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        self.desc_text = tk.Text(desc_container, height=6, font=theme.FONT_BODY, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, relief="flat", padx=8, pady=8)
        self.desc_text.pack(fill="both", expand=True)
        row += 2

        # Time Tracking Section (Both for Editing and New Issue initial log)
        worklog_box = tk.LabelFrame(
            self.form,
            text="  Time Tracking & Worklogs  ",
            font=theme.FONT_SECTION,
            fg=theme.COLOR_TEXT_PRIMARY,
            bg=theme.COLOR_SURFACE,
            padx=12,
            pady=10
        )
        worklog_box.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        row += 1

        input_frame = tk.Frame(worklog_box, bg=theme.COLOR_SURFACE)
        input_frame.pack(fill="x", pady=(0, 8))

        tk.Label(input_frame, text="Time Spent:", font=theme.FONT_BODY, bg=theme.COLOR_SURFACE).pack(side="left", padx=(0, 6))
        self.time_val_entry = tk.Entry(input_frame, width=6, font=theme.FONT_BODY, relief="solid", bd=1)
        self.time_val_entry.pack(side="left", ipady=3)
        self.time_val_entry.insert(0, "30")

        self.time_unit_combo = ttk.Combobox(input_frame, state="readonly", values=["Minutes", "Hours"], width=8, font=theme.FONT_BODY)
        self.time_unit_combo.current(0)
        self.time_unit_combo.pack(side="left", padx=(4, 12))

        tk.Label(input_frame, text="Notes:", font=theme.FONT_BODY, bg=theme.COLOR_SURFACE).pack(side="left", padx=(0, 6))
        self.worklog_notes_entry = tk.Entry(input_frame, font=theme.FONT_BODY, relief="solid", bd=1)
        self.worklog_notes_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)

        if self.issue:
            log_btn = tk.Button(
                input_frame,
                text="+ Log Time",
                font=theme.FONT_CAPTION,
                bg=theme.COLOR_BLUE_LIGHT,
                fg=theme.COLOR_BLUE,
                relief="flat",
                cursor="hand2",
                command=self._add_worklog
            )
            log_btn.pack(side="right", padx=4)

            self.worklogs_listbox = tk.Listbox(
                worklog_box,
                height=4,
                font=theme.FONT_CAPTION,
                bg=theme.COLOR_CARD,
                fg=theme.COLOR_TEXT_SECONDARY,
                relief="solid",
                bd=1
            )
            self.worklogs_listbox.pack(fill="x", pady=(4, 0))
            self._refresh_worklogs()
        else:
            # For new issues, time entered here will be saved when issue is created
            tk.Label(
                worklog_box,
                text="ℹ️ Time entered above will be logged upon saving this new issue.",
                font=theme.FONT_CAPTION,
                fg=theme.COLOR_TEXT_MUTED,
                bg=theme.COLOR_SURFACE
            ).pack(anchor="w", pady=(2, 0))

        self.form.columnconfigure(0, weight=1)
        self.form.columnconfigure(1, weight=1)

        v_scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        # Bottom Action Bar
        bottom_bar = tk.Frame(self, bg=theme.COLOR_CARD, padx=20, pady=12, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        bottom_bar.pack(fill="x", side="bottom")

        tk.Label(
            bottom_bar,
            text="Tip: Press Ctrl+Enter to Save, Esc to Cancel",
            font=theme.FONT_CAPTION,
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_CARD
        ).pack(side="left")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", style="Secondary.TButton", command=self.destroy)
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ttk.Button(bottom_bar, text="Save Issue", style="Primary.TButton", command=self._save_issue)
        save_btn.pack(side="right")

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
                note_str = f" - {l.notes}" if l.notes else ""
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
            # Fallback to match text
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
