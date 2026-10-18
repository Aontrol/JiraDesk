"""
Responsive Google Material Kanban Board View for JiraDesk.
Features grid-stabilized scrollable columns, autohiding scrollbars, and modern empty states.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Dict
from models import Issue, Status
from ui.card_widget import CardWidget
import theme


class KanbanView(tk.Frame):
    def __init__(self, parent, statuses: List[Status],
                 on_open_issue: Callable[[int], None],
                 on_status_change: Callable[[int, int], None],
                 on_delete_issue: Callable[[int], None],
                 on_log_time: Callable[[int], None],
                 on_create_issue_with_status: Callable[[int], None]):
        super().__init__(parent, bg=theme.COLOR_SURFACE)
        self.statuses = statuses
        self.on_open_issue = on_open_issue
        self.on_status_change = on_status_change
        self.on_delete_issue = on_delete_issue
        self.on_log_time = on_log_time
        self.on_create_issue_with_status = on_create_issue_with_status

        self.column_cards_frames: Dict[int, tk.Frame] = {}
        self.column_canvases: Dict[int, tk.Canvas] = {}
        self.column_scrollbars: Dict[int, ttk.Scrollbar] = {}
        self.column_count_labels: Dict[int, tk.Label] = {}

        self._build_board()

    def _build_board(self):
        # Outer Canvas for Horizontal Board Scrolling
        self.canvas = tk.Canvas(self, bg=theme.COLOR_SURFACE, highlightthickness=0)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.columns_container = tk.Frame(self.canvas, bg=theme.COLOR_SURFACE, padx=14, pady=12)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.columns_container, anchor="nw")

        # Keep canvas scrollregion updated and handle window resize
        self.columns_container.bind("<Configure>", self._on_container_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Global horizontal mouse wheel binding on board
        self.canvas.bind("<MouseWheel>", self._on_horizontal_wheel)
        self.columns_container.bind("<MouseWheel>", self._on_horizontal_wheel)

        self.columns_container.grid_rowconfigure(0, weight=1)

        # Build each status column
        for idx, status in enumerate(self.statuses):
            self.columns_container.grid_columnconfigure(idx, weight=1, minsize=260)

            col_outer = tk.Frame(
                self.columns_container,
                bg=theme.COLOR_HOVER,
                highlightbackground=theme.COLOR_BORDER,
                highlightthickness=1,
                width=260
            )
            col_outer.grid(row=0, column=idx, padx=6, pady=4, sticky="nsew")

            # Colored Top Accent Bar (3px)
            accent_bar = tk.Frame(col_outer, bg=status.color, height=3)
            accent_bar.pack(fill="x")

            # Column Header
            header = tk.Frame(col_outer, bg=theme.COLOR_CARD, padx=12, pady=10)
            header.pack(fill="x")

            dot = tk.Label(header, text="●", font=(theme.FONT_FAMILY, 10), fg=status.color, bg=theme.COLOR_CARD)
            dot.pack(side="left", padx=(0, 6))

            title_lbl = tk.Label(header, text=status.name, font=theme.FONT_SECTION, fg=theme.COLOR_TEXT_PRIMARY, bg=theme.COLOR_CARD)
            title_lbl.pack(side="left")

            count_lbl = tk.Label(
                header,
                text="0",
                font=theme.FONT_BADGE,
                fg=theme.COLOR_TEXT_SECONDARY,
                bg=theme.COLOR_HOVER,
                padx=7,
                pady=2
            )
            count_lbl.pack(side="left", padx=8)
            self.column_count_labels[status.id] = count_lbl

            # "+ Add" Quick Button in Header
            add_btn = tk.Label(
                header,
                text="+ Add",
                font=theme.FONT_CAPTION,
                fg=theme.COLOR_BLUE,
                bg=theme.COLOR_BLUE_LIGHT,
                cursor="hand2",
                padx=8,
                pady=2
            )
            add_btn.pack(side="right")
            add_btn.bind("<Button-1>", lambda e, sid=status.id: self.on_create_issue_with_status(sid))
            add_btn.bind("<Enter>", lambda e, b=add_btn: b.configure(bg=theme.COLOR_BLUE, fg=theme.COLOR_TEXT_WHITE))
            add_btn.bind("<Leave>", lambda e, b=add_btn: b.configure(bg=theme.COLOR_BLUE_LIGHT, fg=theme.COLOR_BLUE))

            divider = tk.Frame(col_outer, bg=theme.COLOR_BORDER, height=1)
            divider.pack(fill="x")

            # Grid-stabilized cards body area (prevents layout shifts on scrollbar toggle)
            cards_body = tk.Frame(col_outer, bg=theme.COLOR_HOVER)
            cards_body.pack(fill="both", expand=True)

            cards_body.grid_rowconfigure(0, weight=1)
            cards_body.grid_columnconfigure(0, weight=1)

            col_canvas = tk.Canvas(cards_body, bg=theme.COLOR_HOVER, highlightthickness=0)
            col_v_scroll = ttk.Scrollbar(cards_body, orient="vertical", command=col_canvas.yview)
            col_canvas.configure(yscrollcommand=col_v_scroll.set)

            cards_frame = tk.Frame(col_canvas, bg=theme.COLOR_HOVER, padx=6, pady=8)
            col_window = col_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

            col_canvas.grid(row=0, column=0, sticky="nsew")
            col_v_scroll.grid(row=0, column=1, sticky="ns")
            col_v_scroll.grid_remove()  # Initially hidden until overflow

            col_canvas.bind(
                "<Configure>",
                lambda e, c=col_canvas, w=col_window: c.itemconfig(w, width=e.width)
            )

            # Clean helper to autohide/show scrollbar without packing jitter
            def _check_scroll(e=None, c=col_canvas, s=col_v_scroll, f=cards_frame):
                c.configure(scrollregion=c.bbox("all"))
                bbox = c.bbox("all")
                if bbox and (bbox[3] - bbox[1]) > c.winfo_height() and c.winfo_height() > 50:
                    s.grid()
                else:
                    s.grid_remove()

            cards_frame.bind("<Configure>", _check_scroll)
            col_canvas.bind("<Configure>", _check_scroll)

            # Bind vertical mouse wheel to column canvas & card frame
            col_canvas.bind("<MouseWheel>", lambda e, c=col_canvas: c.yview_scroll(-1 if e.delta > 0 else 1, "units"))
            cards_frame.bind("<MouseWheel>", lambda e, c=col_canvas: c.yview_scroll(-1 if e.delta > 0 else 1, "units"))

            self.column_canvases[status.id] = col_canvas
            self.column_cards_frames[status.id] = cards_frame
            self.column_scrollbars[status.id] = col_v_scroll

    def _on_container_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        canvas_height = event.height
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, height=canvas_height)
        min_width = len(self.statuses) * 272 + 28
        if canvas_width > min_width:
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        else:
            self.canvas.itemconfig(self.canvas_window, width=min_width)

    def _on_horizontal_wheel(self, event):
        self.canvas.xview_scroll(-1 if event.delta > 0 else 1, "units")

    def populate(self, issues: List[Issue]):
        """Clear and repopulate all Kanban cards with empty-state indicators."""
        for status_id, frame in self.column_cards_frames.items():
            for child in frame.winfo_children():
                child.destroy()
            self.column_count_labels[status_id].configure(text="0")

        counts: Dict[int, int] = {s.id: 0 for s in self.statuses}
        for issue in issues:
            if issue.status_id in self.column_cards_frames:
                target_frame = self.column_cards_frames[issue.status_id]
                card = CardWidget(
                    target_frame,
                    issue=issue,
                    statuses=self.statuses,
                    on_open_issue=self.on_open_issue,
                    on_status_change=self.on_status_change,
                    on_delete_issue=self.on_delete_issue,
                    on_log_time=self.on_log_time
                )
                card.pack(fill="x", pady=4, padx=2)
                counts[issue.status_id] = counts.get(issue.status_id, 0) + 1

        # Update counter badges and add clean placeholder if empty
        for s in self.statuses:
            count = counts.get(s.id, 0)
            self.column_count_labels[s.id].configure(text=str(count))
            if count == 0 and s.id in self.column_cards_frames:
                frame = self.column_cards_frames[s.id]
                empty_box = tk.Frame(
                    frame,
                    bg=theme.COLOR_CARD,
                    highlightbackground=theme.COLOR_BORDER,
                    highlightthickness=1,
                    padx=14,
                    pady=20
                )
                empty_box.pack(fill="x", pady=10, padx=4)

                tk.Label(
                    empty_box,
                    text="📋",
                    font=(theme.FONT_FAMILY, 18),
                    bg=theme.COLOR_CARD,
                    fg=theme.COLOR_TEXT_MUTED
                ).pack(pady=(0, 4))

                tk.Label(
                    empty_box,
                    text=f"No {s.name} tasks",
                    font=theme.FONT_BODY_BOLD,
                    fg=theme.COLOR_TEXT_SECONDARY,
                    bg=theme.COLOR_CARD
                ).pack()

                tk.Label(
                    empty_box,
                    text="Tasks in this column will appear here",
                    font=theme.FONT_CAPTION,
                    fg=theme.COLOR_TEXT_MUTED,
                    bg=theme.COLOR_CARD
                ).pack(pady=(2, 8))

                add_link = tk.Label(
                    empty_box,
                    text="+ Create task here",
                    font=theme.FONT_BADGE,
                    fg=theme.COLOR_BLUE,
                    bg=theme.COLOR_BLUE_LIGHT,
                    padx=10,
                    pady=4,
                    cursor="hand2"
                )
                add_link.pack()
                add_link.bind("<Button-1>", lambda e, sid=s.id: self.on_create_issue_with_status(sid))
                add_link.bind("<Enter>", lambda e, b=add_link: b.configure(bg=theme.COLOR_BLUE, fg=theme.COLOR_TEXT_WHITE))
                add_link.bind("<Leave>", lambda e, b=add_link: b.configure(bg=theme.COLOR_BLUE_LIGHT, fg=theme.COLOR_BLUE))
