"""
List / Table Backlog View for JiraDesk with interactive sorting & zebra striping.
Features non-overlapping grid scrollbars, dynamic title stretching, and modern empty states.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Dict
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

        self.issues_by_iid: Dict[str, Issue] = {}
        self.sort_column = "key"
        self.sort_descending = False

        self.base_headers = {
            "key": "Key",
            "type": "Type",
            "title": "Summary",
            "priority": "Priority",
            "status": "Status",
            "time": "Logged Time",
            "created": "Created"
        }

        self._build_table()

    def _build_table(self):
        self.container = tk.Frame(self, bg=theme.COLOR_CARD, highlightbackground=theme.COLOR_BORDER, highlightthickness=1)
        self.container.pack(fill="both", expand=True, padx=16, pady=12)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        columns = ("key", "type", "title", "priority", "status", "time", "created")
        self.tree = ttk.Treeview(
            self.container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Alternating row tag colors (zebra striping)
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("evenrow", background="#f8f9fa")

        widths = {
            "key": 95,
            "type": 105,
            "title": 420,
            "priority": 110,
            "status": 125,
            "time": 115,
            "created": 125,
        }

        for col_id, heading_text in self.base_headers.items():
            self.tree.heading(col_id, text=heading_text, anchor="w", command=lambda c=col_id: self._sort_by(c))
            # Summary title stretches to absorb window resizing; others remain fixed
            should_stretch = (col_id == "title")
            self.tree.column(col_id, width=widths.get(col_id, 100), minwidth=70, stretch=should_stretch)

        v_scroll = ttk.Scrollbar(self.container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self.container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Non-overlapping grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Empty state banner frame
        self.empty_frame = tk.Frame(self.container, bg=theme.COLOR_CARD)
        tk.Label(self.empty_frame, text="🔍", font=(theme.FONT_FAMILY, 24), bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_MUTED).pack(pady=(0, 6))
        tk.Label(self.empty_frame, text="No issues found", font=theme.FONT_SUBTITLE, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD).pack()
        tk.Label(self.empty_frame, text="Try adjusting your project filter or search keywords", font=theme.FONT_CAPTION, fg=theme.COLOR_TEXT_MUTED, bg=theme.COLOR_CARD).pack(pady=(2, 0))

        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

    def populate(self, issues: List[Issue]):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.issues_by_iid.clear()

        if not issues:
            self.empty_frame.grid(row=0, column=0, sticky="nsew")
            return
        else:
            self.empty_frame.grid_forget()

        for idx, issue in enumerate(issues):
            created_short = issue.created_at[:10] if issue.created_at else ""
            time_display = f"⏱ {issue.formatted_time}" if issue.formatted_time else "—"

            type_conf = theme.TYPE_CONFIG.get(issue.issue_type, {"icon": "•"})
            type_formatted = f"{type_conf['icon']} {issue.issue_type}"

            prio_conf = theme.PRIORITY_CONFIG.get(issue.priority, {"icon": "•"})
            prio_formatted = f"{prio_conf['icon']} {issue.priority}"

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            iid = self.tree.insert(
                "",
                "end",
                values=(
                    issue.key,
                    type_formatted,
                    issue.title,
                    prio_formatted,
                    issue.status_name,
                    time_display,
                    created_short
                ),
                tags=(tag,)
            )
            self.issues_by_iid[iid] = issue

        self._update_header_indicators()

    def _update_header_indicators(self):
        """Updates header text to show ▲ or ▼ on the sorted column."""
        for col_id, base_text in self.base_headers.items():
            if col_id == self.sort_column:
                indicator = " ▲" if not self.sort_descending else " ▼"
                self.tree.heading(col_id, text=f"{base_text}{indicator}")
            else:
                self.tree.heading(col_id, text=base_text)

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
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(child, tags=(tag,))

        self._update_header_indicators()

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
            menu.add_command(label="✏️  Open / Edit Issue", command=lambda: self.on_open_issue(issue.id))
            menu.add_command(label="⏱  Log Work Time", command=lambda: self.on_log_time(issue.id))
            menu.add_separator()

            status_menu = tk.Menu(menu, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
            for s in self.statuses:
                if s.id != issue.status_id:
                    status_menu.add_command(
                        label=f"Move to {s.name}",
                        command=lambda sid=s.id: self.on_status_change(issue.id, sid)
                    )
            menu.add_cascade(label="↗️  Move to Status...", menu=status_menu)

            menu.add_separator()
            menu.add_command(label="🗑️  Delete Issue", command=lambda: self.on_delete_issue(issue.id))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
