"""
Polished Google Material-styled Kanban card widget with 1-click status transitions.
"""
import tkinter as tk
from typing import Callable, List
from models import Issue, Status
import theme


class CardWidget(tk.Frame):
    def __init__(self, parent, issue: Issue, statuses: List[Status],
                 on_open_issue: Callable[[int], None],
                 on_status_change: Callable[[int, int], None],
                 on_delete_issue: Callable[[int], None],
                 on_log_time: Callable[[int], None]):
        super().__init__(
            parent,
            bg=theme.COLOR_CARD,
            highlightbackground=theme.COLOR_BORDER,
            highlightthickness=1,
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.issue = issue
        self.statuses = statuses
        self.on_open_issue = on_open_issue
        self.on_status_change = on_status_change
        self.on_delete_issue = on_delete_issue
        self.on_log_time = on_log_time

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        # Row 1: Key, Type badge, Priority badge
        top_row = tk.Frame(self, bg=theme.COLOR_CARD)
        top_row.pack(fill="x", pady=(0, 6))

        # Issue Key (e.g. DEV-101)
        key_lbl = tk.Label(
            top_row,
            text=self.issue.key,
            font=theme.FONT_BADGE,
            fg=theme.COLOR_BLUE,
            bg=theme.COLOR_BLUE_LIGHT,
            padx=6,
            pady=2
        )
        key_lbl.pack(side="left")

        # Type badge with icon (e.g., 📋 Task)
        type_conf = theme.TYPE_CONFIG.get(self.issue.issue_type, {"icon": "•", "fg": theme.COLOR_TEXT_SECONDARY, "bg": theme.COLOR_HOVER})
        type_lbl = tk.Label(
            top_row,
            text=f"{type_conf['icon']} {self.issue.issue_type}",
            font=theme.FONT_BADGE,
            fg=type_conf["fg"],
            bg=type_conf["bg"],
            padx=5,
            pady=2
        )
        type_lbl.pack(side="left", padx=4)

        # Priority badge with icon (e.g., 🟠 High)
        prio_conf = theme.PRIORITY_CONFIG.get(self.issue.priority, {"icon": "•", "fg": theme.COLOR_TEXT_SECONDARY, "bg": theme.COLOR_HOVER})
        prio_lbl = tk.Label(
            top_row,
            text=f"{prio_conf['icon']} {self.issue.priority}",
            font=theme.FONT_BADGE,
            fg=prio_conf["fg"],
            bg=prio_conf["bg"],
            padx=5,
            pady=2
        )
        prio_lbl.pack(side="right")

        # Row 2: Title / Summary (wrapped cleanly)
        title_lbl = tk.Label(
            self,
            text=self.issue.title,
            font=theme.FONT_BODY_BOLD,
            fg=theme.COLOR_TEXT_PRIMARY,
            bg=theme.COLOR_CARD,
            wraplength=210,
            justify="left",
            anchor="w"
        )
        title_lbl.pack(fill="x", pady=(2, 8))

        # Row 3: Meta & Quick Status Move Buttons
        bottom_row = tk.Frame(self, bg=theme.COLOR_CARD)
        bottom_row.pack(fill="x")

        # Time spent indicator if any
        if self.issue.formatted_time:
            time_lbl = tk.Label(
                bottom_row,
                text=f"⏱ {self.issue.formatted_time}",
                font=theme.FONT_CAPTION,
                fg=theme.COLOR_TEXT_SECONDARY,
                bg=theme.COLOR_HOVER,
                padx=5,
                pady=1
            )
            time_lbl.pack(side="left")

        # Action controls on bottom right
        action_box = tk.Frame(bottom_row, bg=theme.COLOR_CARD)
        action_box.pack(side="right")

        # 1-Click Status Navigation (Left / Right Arrow)
        curr_status_idx = -1
        for idx, s in enumerate(self.statuses):
            if s.id == self.issue.status_id:
                curr_status_idx = idx
                break

        # Previous status arrow button (◀)
        if curr_status_idx > 0:
            prev_status = self.statuses[curr_status_idx - 1]
            btn_prev = tk.Label(
                action_box,
                text="◀",
                font=(theme.FONT_FAMILY, 9, "bold"),
                fg=theme.COLOR_TEXT_SECONDARY,
                bg=theme.COLOR_HOVER,
                padx=5,
                pady=1,
                cursor="hand2"
            )
            btn_prev.pack(side="left", padx=(0, 2))
            btn_prev.bind("<Button-1>", lambda e, sid=prev_status.id: self.on_status_change(self.issue.id, sid))

        # Next status arrow button (▶)
        if curr_status_idx >= 0 and curr_status_idx < len(self.statuses) - 1:
            next_status = self.statuses[curr_status_idx + 1]
            btn_next = tk.Label(
                action_box,
                text="▶",
                font=(theme.FONT_FAMILY, 9, "bold"),
                fg=theme.COLOR_BLUE,
                bg=theme.COLOR_BLUE_LIGHT,
                padx=5,
                pady=1,
                cursor="hand2"
            )
            btn_next.pack(side="left", padx=(0, 4))
            btn_next.bind("<Button-1>", lambda e, sid=next_status.id: self.on_status_change(self.issue.id, sid))

        # "⋮" Action Menu Button
        more_btn = tk.Label(
            action_box,
            text="⋮",
            font=(theme.FONT_FAMILY, 12, "bold"),
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_CARD,
            cursor="hand2",
            padx=2
        )
        more_btn.pack(side="left")
        more_btn.bind("<Button-1>", self._show_context_menu)

    def _bind_events(self):
        # Attach hover and click events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Double-Button-1>", lambda e: self.on_open_issue(self.issue.id))
        self.bind("<Button-3>", self._show_context_menu)

        for child in self.winfo_children():
            if not isinstance(child, tk.Frame):
                child.bind("<Double-Button-1>", lambda e: self.on_open_issue(self.issue.id))
                child.bind("<Button-3>", self._show_context_menu)

    def _on_enter(self, event=None):
        self.configure(highlightbackground=theme.COLOR_BLUE, highlightthickness=1)

    def _on_leave(self, event):
        # Reliable cursor containment check prevents child hover flicker
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget is not None and (widget == self or str(widget).startswith(str(self))):
            return
        self.configure(highlightbackground=theme.COLOR_BORDER, highlightthickness=1)

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
        menu.add_command(label="Open / Edit Issue", command=lambda: self.on_open_issue(self.issue.id))
        menu.add_command(label="Log Work Time", command=lambda: self.on_log_time(self.issue.id))
        menu.add_separator()

        status_menu = tk.Menu(menu, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
        for s in self.statuses:
            if s.id != self.issue.status_id:
                status_menu.add_command(
                    label=f"Move to {s.name}",
                    command=lambda sid=s.id: self.on_status_change(self.issue.id, sid)
                )
        menu.add_cascade(label="Move to Status...", menu=status_menu)

        menu.add_separator()
        menu.add_command(label="Delete Issue", command=lambda: self.on_delete_issue(self.issue.id))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
