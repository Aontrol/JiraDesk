"""
List / Table Backlog View for JiraDesk with interactive sorting.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Callable
from models import Issue, Status
import theme


class TableView(tk.Frame):
    def __init__(self, parent, statuses: List[Status],
                 on_open_issue: Callable[[int], None],
                 on_status_change: Callable[[int, int], None],
                 on_delete_issue: Callable[[int], None],
                 on_log_time: Callable[[int], None]):
        super().__init__(parent, bg=theme.COLOR_SURFACE)
        self.statuses = statuses
        self.on_open_issue = on_open_issue
        self.on_status_change = on_status_change
        self.on_delete_issue = on_delete_issue
        self.on_log_time = on_log_time

        self.issues_by_iid = {}
        self.sort_column = "key"
        self.sort_descending = False

        self._build_table()

    def _build_table(self):
        container = tk.Frame(self, bg=theme.COLOR_CARD, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        columns = ("key", "type", "title", "priority", "status", "time", "created")
        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = [
            ("key", "Key", 90),
            ("type", "Type", 90),
            ("title", "Summary", 420),
            ("priority", "Priority", 100),
            ("status", "Status", 120),
            ("time", "Logged Time", 110),
            ("created", "Created", 130),
        ]

        for col_id, heading_text, width in headers:
            self.tree.heading(col_id, text=heading_text, anchor="w", command=lambda c=col_id: self._sort_by(c))
            self.tree.column(col_id, width=width, minwidth=70)

        v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

    def populate(self, issues: List[Issue]):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.issues_by_iid.clear()

        for issue in issues:
            created_short = issue.created_at[:10] if issue.created_at else ""
            time_display = issue.formatted_time if issue.formatted_time else "—"
            iid = self.tree.insert(
                "",
                "end",
                values=(
                    issue.key,
                    issue.issue_type,
                    issue.title,
                    issue.priority,
                    issue.status_name,
                    time_display,
                    created_short
                )
            )
            self.issues_by_iid[iid] = issue

    def _sort_by(self, col: str):
        """Sort treeview contents when a column heading is clicked."""
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False

        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data.sort(reverse=self.sort_descending)

        for index, (val, child) in enumerate(data):
            self.tree.move(child, "", index)

    def _get_selected_issue(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.issues_by_iid.get(sel[0])

    def _on_double_click(self, event):
        issue = self._get_selected_issue()
        if issue:
            self.on_open_issue(issue.id)

    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            issue = self.issues_by_iid.get(item)
            if not issue:
                return

            menu = tk.Menu(self, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
            menu.add_command(label="Open / Edit Issue", command=lambda: self.on_open_issue(issue.id))
            menu.add_command(label="Log Work Time", command=lambda: self.on_log_time(issue.id))
            menu.add_separator()

            status_menu = tk.Menu(menu, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
            for s in self.statuses:
                if s.id != issue.status_id:
                    status_menu.add_command(
                        label=f"Move to {s.name}",
                        command=lambda sid=s.id: self.on_status_change(issue.id, sid)
                    )
            menu.add_cascade(label="Move to Status...", menu=status_menu)

            menu.add_separator()
            menu.add_command(label="Delete Issue", command=lambda: self.on_delete_issue(issue.id))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
