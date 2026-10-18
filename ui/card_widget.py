"""
Polished Google Material-styled Kanban card widget with 1-click status transitions.
Features dynamic responsive wraplength, smooth hover transitions, and universal double-click.
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

        self.interactive_action_widgets = set()

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        # Row 1: Key, Type badge, Priority badge
        top_row = tk.Frame(self, bg=theme.COLOR_CARD)
        top_row.pack(fill="x", pady=(0, 6))

        # Issue Key (e.g. DEV-101)
        self.key_lbl = tk.Label(
            top_row,
            text=self.issue.key,
            font=theme.FONT_BADGE,
            fg=theme.COLOR_BLUE,
            bg=theme.COLOR_BLUE_LIGHT,
            padx=6,
            pady=2
        )
        self.key_lbl.pack(side="left")

        # Type badge with icon (e.g., 📋 Task)
        type_conf = theme.TYPE_CONFIG.get(self.issue.issue_type, {"icon": "•", "fg": theme.COLOR_TEXT_SECONDARY, "bg": theme.COLOR_HOVER})
        self.type_lbl = tk.Label(
            top_row,
            text=f"{type_conf['icon']} {self.issue.issue_type}",
            font=theme.FONT_BADGE,
            fg=type_conf["fg"],
            bg=type_conf["bg"],
            padx=6,
            pady=2
        )
        self.type_lbl.pack(side="left", padx=4)

        # Priority badge with icon (e.g., 🟠 High)
        prio_conf = theme.PRIORITY_CONFIG.get(self.issue.priority, {"icon": "•", "fg": theme.COLOR_TEXT_SECONDARY, "bg": theme.COLOR_HOVER})
        self.prio_lbl = tk.Label(
            top_row,
            text=f"{prio_conf['icon']} {self.issue.priority}",
            font=theme.FONT_BADGE,
            fg=prio_conf["fg"],
            bg=prio_conf["bg"],
            padx=6,
            pady=2
        )
        self.prio_lbl.pack(side="right")

        # Row 2: Title / Summary (dynamically wrapping to card width)
        self.title_lbl = tk.Label(
            self,
            text=self.issue.title,
            font=theme.FONT_BODY_BOLD,
            fg=theme.COLOR_TEXT_PRIMARY,
            bg=theme.COLOR_CARD,
            wraplength=230,
            justify="left",
            anchor="w"
        )
        self.title_lbl.pack(fill="x", pady=(2, 8))

        # Row 3: Meta & Quick Status Move Buttons
        bottom_row = tk.Frame(self, bg=theme.COLOR_CARD)
        bottom_row.pack(fill="x")

        # Time spent indicator if any
        if self.issue.formatted_time:
            self.time_lbl = tk.Label(
                bottom_row,
                text=f"⏱ {self.issue.formatted_time}",
                font=theme.FONT_CAPTION,
                fg=theme.COLOR_TEXT_SECONDARY,
                bg=theme.COLOR_HOVER,
                padx=6,
                pady=2
            )
            self.time_lbl.pack(side="left")
        else:
            self.time_lbl = None

        # Action controls container on bottom right
        action_box = tk.Frame(bottom_row, bg=theme.COLOR_CARD)
        action_box.pack(side="right")

        # Find status index for 1-click status transitions
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
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn_prev.pack(side="left", padx=(0, 3))
            btn_prev.bind("<Button-1>", lambda e, sid=prev_status.id: self.on_status_change(self.issue.id, sid))
            btn_prev.bind("<Enter>", lambda e, b=btn_prev: b.configure(bg=theme.COLOR_BLUE_LIGHT, fg=theme.COLOR_BLUE))
            btn_prev.bind("<Leave>", lambda e, b=btn_prev: b.configure(bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_SECONDARY))
            self.interactive_action_widgets.add(btn_prev)

        # Next status arrow button (▶)
        if curr_status_idx >= 0 and curr_status_idx < len(self.statuses) - 1:
            next_status = self.statuses[curr_status_idx + 1]
            btn_next = tk.Label(
                action_box,
                text="▶",
                font=(theme.FONT_FAMILY, 9, "bold"),
                fg=theme.COLOR_BLUE,
                bg=theme.COLOR_BLUE_LIGHT,
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn_next.pack(side="left", padx=(0, 4))
            btn_next.bind("<Button-1>", lambda e, sid=next_status.id: self.on_status_change(self.issue.id, sid))
            btn_next.bind("<Enter>", lambda e, b=btn_next: b.configure(bg=theme.COLOR_BLUE, fg=theme.COLOR_TEXT_WHITE))
            btn_next.bind("<Leave>", lambda e, b=btn_next: b.configure(bg=theme.COLOR_BLUE_LIGHT, fg=theme.COLOR_BLUE))
            self.interactive_action_widgets.add(btn_next)

        # "⋮" Action Menu Button
        more_btn = tk.Label(
            action_box,
            text="⋮",
            font=(theme.FONT_FAMILY, 12, "bold"),
            fg=theme.COLOR_TEXT_MUTED,
            bg=theme.COLOR_CARD,
            cursor="hand2",
            padx=4,
            pady=1
        )
        more_btn.pack(side="left")
        more_btn.bind("<Button-1>", self._show_context_menu)
        more_btn.bind("<Enter>", lambda e, b=more_btn: b.configure(bg=theme.COLOR_HOVER, fg=theme.COLOR_TEXT_PRIMARY))
        more_btn.bind("<Leave>", lambda e, b=more_btn: b.configure(bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_MUTED))
        self.interactive_action_widgets.add(more_btn)

    def _bind_events(self):
        # Dynamically adapt title wraplength when card width changes
        self.bind("<Configure>", self._on_configure)

        # Attach hover, click, and context menu across all card components
        self._bind_recursive(self)

    def _bind_recursive(self, widget):
        if widget not in self.interactive_action_widgets:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<Double-Button-1>", lambda e: self.on_open_issue(self.issue.id))
            widget.bind("<Button-3>", self._show_context_menu)

        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_configure(self, event):
        # Ensure title wraps to current card width (minus 28px padding)
        new_wrap = max(180, event.width - 28)
        self.title_lbl.configure(wraplength=new_wrap)

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
        menu.add_command(label="✏️  Open / Edit Issue", command=lambda: self.on_open_issue(self.issue.id))
        menu.add_command(label="⏱  Log Work Time", command=lambda: self.on_log_time(self.issue.id))
        menu.add_separator()

        status_menu = tk.Menu(menu, tearoff=0, bg=theme.COLOR_CARD, fg=theme.COLOR_TEXT_PRIMARY, font=theme.FONT_BODY)
        for s in self.statuses:
            if s.id != self.issue.status_id:
                status_menu.add_command(
                    label=f"Move to {s.name}",
                    command=lambda sid=s.id: self.on_status_change(self.issue.id, sid)
                )
        menu.add_cascade(label="↗️  Move to Status...", menu=status_menu)

        menu.add_separator()
        menu.add_command(label="🗑️  Delete Issue", command=lambda: self.on_delete_issue(self.issue.id))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
