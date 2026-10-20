import os
import sys
import time
import threading
import tkinter as tk
import customtkinter as ctk
from typing import List, Optional

from src.port_scanner import scan_ports, PortItem
from src.process_manager import terminate_process_by_pid, ProcessResult
from src.security import is_admin, restart_as_admin
from src.ui.theme import COLORS, get_status_color
from src.ui.components import StatCard, ConfirmStopDialog, AdminNoticeDialog

# Set overall appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PortViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Port Viewer • Windows Port & Process Manager")
        self.geometry("1120x720")
        self.minsize(880, 560)
        self.configure(fg_color=COLORS["bg_dark"])

        # Try setting icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # State
        self.all_items: List[PortItem] = []
        self.filtered_items: List[PortItem] = []
        self.is_scanning: bool = False
        self.current_filter: str = "Listening Only"
        self.search_query: str = ""
        self.auto_refresh_job = None
        self.auto_refresh_sec = 0

        # Sorting state
        self.sort_column: str = "PORT"
        self.sort_ascending: bool = True
        self.col_buttons = {}

        self._build_header()
        self._build_stats_bar()
        self._build_controls_bar()
        self._build_table_area()
        self._build_status_bar()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=64, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Title & Branding
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=20, pady=10)

        app_title = ctk.CTkLabel(
            left_box, text="⚡ Port Viewer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_main"]
        )
        app_title.pack(side="left")

        ver_badge = ctk.CTkLabel(
            left_box, text="v1.0 • Secure",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["card_border"],
            corner_radius=6,
            padx=8, pady=2
        )
        ver_badge.pack(side="left", padx=(10, 0))

        # Admin Badge & Action
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=20, pady=10)

        self.has_admin = is_admin()
        if self.has_admin:
            admin_badge = ctk.CTkLabel(
                right_box, text="🛡️ Administrator Mode",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["success"],
                fg_color="#064E3B",
                corner_radius=6,
                padx=10, pady=4
            )
            admin_badge.pack(side="right")
        else:
            admin_badge = ctk.CTkLabel(
                right_box, text="Standard User",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["warning"],
                fg_color="#451A03",
                corner_radius=6,
                padx=10, pady=4
            )
            admin_badge.pack(side="left", padx=(0, 10))

            elevate_btn = ctk.CTkButton(
                right_box, text="🛡️ Relaunch as Admin",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                height=30,
                command=restart_as_admin
            )
            elevate_btn.pack(side="left")

    def _build_stats_bar(self):
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(16, 8))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_cards")

        self.card_total = StatCard(stats_frame, title="Total Connections", value="--", icon="🌐")
        self.card_total.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.card_listen = StatCard(stats_frame, title="Listening Services", value="--", icon="🎧")
        self.card_listen.grid(row=0, column=1, padx=6, sticky="ew")

        self.card_established = StatCard(stats_frame, title="Established", value="--", icon="🔗")
        self.card_established.grid(row=0, column=2, padx=6, sticky="ew")

        self.card_scantime = StatCard(stats_frame, title="Scan Duration", value="--", icon="⏱️")
        self.card_scantime.grid(row=0, column=3, padx=(6, 0), sticky="ew")

    def _build_controls_bar(self):
        ctrl_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["card_border"])
        ctrl_frame.pack(fill="x", padx=20, pady=8)

        # Main "Check Ports" Button
        self.scan_btn = ctk.CTkButton(
            ctrl_frame, text="🔍 Check Ports",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=40, width=150,
            command=self.start_scan
        )
        self.scan_btn.pack(side="left", padx=12, pady=10)

        # Filter Segmented Button
        self.filter_seg = ctk.CTkSegmentedButton(
            ctrl_frame,
            values=["Listening Only", "All Ports", "TCP Only", "UDP Only"],
            command=self._on_filter_changed,
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            height=36
        )
        self.filter_seg.set("Listening Only")
        self.filter_seg.pack(side="left", padx=10, pady=10)

        # Search Box
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_changed())

        self.search_entry = ctk.CTkEntry(
            ctrl_frame,
            textvariable=self.search_var,
            placeholder_text="Filter by port (e.g. 3000), process name, or PID...",
            width=280,
            height=36
        )
        self.search_entry.pack(side="right", padx=12, pady=10)

        # Auto-refresh selector
        self.auto_refresh_combo = ctk.CTkComboBox(
            ctrl_frame,
            values=["Auto: Off", "Auto: 3s", "Auto: 5s", "Auto: 10s"],
            command=self._on_auto_refresh_changed,
            width=110,
            height=36
        )
        self.auto_refresh_combo.set("Auto: Off")
        self.auto_refresh_combo.pack(side="right", padx=(0, 8), pady=10)

    def _build_table_area(self):
        self.table_container = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["card_border"])
        self.table_container.pack(fill="both", expand=True, padx=20, pady=8)

        # Table Header
        self.table_header = ctk.CTkFrame(self.table_container, fg_color=COLORS["card_border"], height=36, corner_radius=6)
        self.table_header.pack(fill="x", padx=8, pady=(8, 4))
        self.table_header.pack_propagate(False)

        col_defs = [
            ("PROTO", 70, True),
            ("PORT", 85, True),
            ("LOCAL ADDRESS", 150, True),
            ("STATUS", 110, True),
            ("PROCESS NAME", 220, True),
            ("PID", 90, True),
            ("MEMORY", 90, True),
            ("ACTION", 100, False)
        ]

        for title, width, is_sortable in col_defs:
            if is_sortable:
                arrow = " ▲" if title == self.sort_column and self.sort_ascending else (" ▼" if title == self.sort_column else "")
                btn = ctk.CTkButton(
                    self.table_header,
                    text=f"{title}{arrow}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#60A5FA" if title == self.sort_column else COLORS["text_muted"],
                    fg_color=COLORS["card_bg"] if title == self.sort_column else "transparent",
                    hover_color=COLORS["hover_bg"],
                    width=width,
                    height=28,
                    corner_radius=4,
                    anchor="w" if title in ("LOCAL ADDRESS", "PROCESS NAME") else "center",
                    command=lambda t=title: self._on_column_header_clicked(t)
                )
                btn.pack(side="left", padx=4)
                self.col_buttons[title] = btn
            else:
                lbl = ctk.CTkLabel(
                    self.table_header, text=title,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["text_dim"],
                    width=width,
                    anchor="center"
                )
                lbl.pack(side="left", padx=4)

        # Scrollable rows frame
        self.rows_frame = ctk.CTkScrollableFrame(
            self.table_container, fg_color="transparent"
        )
        self.rows_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Landing Hero (visible before initial scan)
        self._show_landing_hero()

    def _show_landing_hero(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.hero_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        self.hero_frame.pack(fill="both", expand=True, pady=60)

        icon_lbl = ctk.CTkLabel(self.hero_frame, text="🌐", font=ctk.CTkFont(size=64))
        icon_lbl.pack(pady=(0, 10))

        title_lbl = ctk.CTkLabel(
            self.hero_frame, text="Ready to Inspect Ports",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_main"]
        )
        title_lbl.pack(pady=(0, 8))

        sub_lbl = ctk.CTkLabel(
            self.hero_frame,
            text="Press 'Check Ports' to detect all active TCP/UDP ports, identify occupying processes,\nand stop unwanted or frozen servers safely.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
            justify="center"
        )
        sub_lbl.pack(pady=(0, 20))

        hero_btn = ctk.CTkButton(
            self.hero_frame, text="🚀 Check Ports Now",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=42, width=180,
            command=self.start_scan
        )
        hero_btn.pack()

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=32, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Ready. Click 'Check Ports' to begin scan.",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]
        )
        self.status_label.pack(side="left", padx=16)

        self.status_count = ctk.CTkLabel(
            self.status_bar, text="",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"]
        )
        self.status_count.pack(side="right", padx=16)

    def start_scan(self):
        """Starts asynchronous background port scan to keep UI responsive."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text="Scanning network sockets and matching processes...")

        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        t0 = time.time()
        # Scan all ports so user can filter without rescanning
        items = scan_ports(filter_listening_only=False)
        duration = time.time() - t0

        # Update UI in main thread
        self.after(0, self._scan_completed, items, duration)

    def _scan_completed(self, items: List[PortItem], duration: float):
        self.is_scanning = False
        self.scan_btn.configure(state="normal", text="🔄 Refresh Ports")
        self.all_items = items

        # Compute stats
        total_count = len(items)
        listen_count = sum(1 for x in items if x.status == "LISTEN")
        estab_count = sum(1 for x in items if x.status == "ESTABLISHED")

        self.card_total.update_value(str(total_count))
        self.card_listen.update_value(str(listen_count))
        self.card_established.update_value(str(estab_count))
        self.card_scantime.update_value(f"{duration:.2f}s")

        self.status_label.configure(
            text=f"Scan complete: {total_count} ports detected in {duration:.2f}s."
        )

        self._apply_filters_and_render()

    def _on_filter_changed(self, value: str):
        self.current_filter = value
        self._apply_filters_and_render()

    def _on_search_changed(self):
        self.search_query = self.search_var.get().strip().lower()
        self._apply_filters_and_render()

    def _on_column_header_clicked(self, col_name: str):
        """Toggle ascending/descending or switch sort column."""
        if self.sort_column == col_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = col_name
            self.sort_ascending = True

        self._update_header_labels()
        self._apply_filters_and_render()

    def _update_header_labels(self):
        """Updates arrow indicators and highlight styles on header buttons."""
        arrow = " ▲" if self.sort_ascending else " ▼"
        for title, btn in self.col_buttons.items():
            if title == self.sort_column:
                btn.configure(
                    text=f"{title}{arrow}",
                    text_color="#60A5FA",
                    fg_color=COLORS["card_bg"]
                )
            else:
                btn.configure(
                    text=title,
                    text_color=COLORS["text_muted"],
                    fg_color="transparent"
                )

    def _sort_items(self, items: List[PortItem]) -> List[PortItem]:
        """Sorts PortItem list based on active column and direction."""
        col = self.sort_column
        asc = self.sort_ascending

        if col == "PROTO":
            key_fn = lambda x: (x.protocol or "", x.local_port)
        elif col == "PORT":
            key_fn = lambda x: (x.local_port, x.protocol)
        elif col == "LOCAL ADDRESS":
            key_fn = lambda x: (x.local_ip or "", x.local_port)
        elif col == "STATUS":
            key_fn = lambda x: (x.status or "", x.local_port)
        elif col == "PROCESS NAME":
            key_fn = lambda x: ((x.process_name or "").lower(), x.local_port)
        elif col == "PID":
            key_fn = lambda x: (x.pid if x.pid is not None else -1, x.local_port)
        elif col == "MEMORY":
            key_fn = lambda x: (x.memory_mb, x.local_port)
        else:
            key_fn = lambda x: (x.local_port, x.protocol)

        return sorted(items, key=key_fn, reverse=not asc)

    def _apply_filters_and_render(self):
        if not self.all_items:
            return

        filtered = []
        for it in self.all_items:
            # 1. Filter category
            if self.current_filter == "Listening Only" and it.status != "LISTEN":
                continue
            elif self.current_filter == "TCP Only" and it.protocol != "TCP":
                continue
            elif self.current_filter == "UDP Only" and it.protocol != "UDP":
                continue

            # 2. Search query (matches Port, Process Name, or PID)
            if self.search_query:
                port_str = str(it.local_port)
                pid_str = str(it.pid) if it.pid else ""
                name_str = it.process_name.lower()
                ip_str = it.local_ip.lower()
                if (self.search_query not in port_str and
                    self.search_query not in pid_str and
                    self.search_query not in name_str and
                    self.search_query not in ip_str):
                    continue

            filtered.append(it)

        # Apply column sorting
        self.filtered_items = self._sort_items(filtered)
        self._render_rows()

    def _render_rows(self):
        # Clear existing row widgets
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if not self.filtered_items:
            empty_lbl = ctk.CTkLabel(
                self.rows_frame,
                text="No matching ports found for current filter or search criteria.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"]
            )
            empty_lbl.pack(pady=40)
            self.status_count.configure(text="Showing 0 results")
            return

        self.status_count.configure(text=f"Showing {len(self.filtered_items)} of {len(self.all_items)} ports")

        # Render rows
        for idx, item in enumerate(self.filtered_items):
            bg = COLORS["card_bg"] if idx % 2 == 0 else "#162032"
            row = ctk.CTkFrame(self.rows_frame, fg_color=bg, height=40, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # Protocol badge
            proto_color = COLORS["primary"] if item.protocol == "TCP" else COLORS["purple"]
            p_lbl = ctk.CTkLabel(
                row, text=item.protocol,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=proto_color,
                width=70
            )
            p_lbl.pack(side="left", padx=4)

            # Port badge
            port_lbl = ctk.CTkLabel(
                row, text=str(item.local_port),
                font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
                text_color=COLORS["text_main"],
                width=85
            )
            port_lbl.pack(side="left", padx=4)

            # Local address
            addr_text = f"{item.local_ip}:{item.local_port}" if item.local_ip else f":{item.local_port}"
            if len(addr_text) > 18:
                addr_text = addr_text[:17] + "…"
            addr_lbl = ctk.CTkLabel(
                row, text=addr_text,
                font=ctk.CTkFont(size=11, family="Consolas"),
                text_color=COLORS["text_muted"],
                width=150, anchor="w"
            )
            addr_lbl.pack(side="left", padx=4)

            # Status
            st_color = get_status_color(item.status)
            st_lbl = ctk.CTkLabel(
                row, text=item.status,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=st_color,
                width=110
            )
            st_lbl.pack(side="left", padx=4)

            # Process Name
            pname = item.process_name
            if len(pname) > 26:
                pname = pname[:24] + "…"
            name_lbl = ctk.CTkLabel(
                row, text=pname,
                font=ctk.CTkFont(size=11, weight="bold" if item.pid else "normal"),
                text_color=COLORS["text_main"],
                width=220, anchor="w"
            )
            name_lbl.pack(side="left", padx=4)

            # PID
            pid_str = str(item.pid) if item.pid is not None else "-"
            pid_lbl = ctk.CTkLabel(
                row, text=pid_str,
                font=ctk.CTkFont(size=11, family="Consolas"),
                text_color=COLORS["text_muted"],
                width=90
            )
            pid_lbl.pack(side="left", padx=4)

            # Memory
            mem_str = f"{item.memory_mb:.1f} MB" if item.memory_mb > 0 else "-"
            mem_lbl = ctk.CTkLabel(
                row, text=mem_str,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_dim"],
                width=90
            )
            mem_lbl.pack(side="left", padx=4)

            # Action: Stop button
            if item.is_critical or item.pid in (None, 0, 4):
                # Critical system processes cannot be stopped to prevent BSOD
                prot_lbl = ctk.CTkLabel(
                    row, text="🔒 System",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_dim"],
                    width=95
                )
                prot_lbl.pack(side="left", padx=4)
            else:
                stop_btn = ctk.CTkButton(
                    row, text="⏹ Stop",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color=COLORS["danger"],
                    hover_color=COLORS["danger_hover"],
                    text_color="#FFFFFF",
                    width=85, height=26,
                    command=lambda it=item: self._on_stop_requested(it)
                )
                stop_btn.pack(side="left", padx=6)

    def _on_stop_requested(self, item: PortItem):
        """Opens security confirmation modal before stopping any process."""
        ConfirmStopDialog(self, item, on_confirm=lambda: self._execute_stop(item))

    def _execute_stop(self, item: PortItem):
        """Executes process termination in background to avoid blocking GUI."""
        if not item.pid:
            return

        self.status_label.configure(text=f"Stopping {item.process_name} (PID: {item.pid})...")
        threading.Thread(target=self._stop_worker, args=(item,), daemon=True).start()

    def _stop_worker(self, item: PortItem):
        res: ProcessResult = terminate_process_by_pid(item.pid, expected_create_time=item.create_time)
        self.after(0, self._stop_completed, res, item)

    def _stop_completed(self, res: ProcessResult, item: PortItem):
        if res.success:
            self.status_label.configure(
                text=f"✅ {res.message}",
                text_color=COLORS["success"]
            )
            # Re-scan to update the view
            self.start_scan()
        else:
            self.status_label.configure(
                text=f"❌ {res.message}",
                text_color=COLORS["danger"]
            )
            if res.requires_admin:
                AdminNoticeDialog(self, res.message)

    def _on_auto_refresh_changed(self, choice: str):
        if self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

        if "3s" in choice:
            self.auto_refresh_sec = 3
        elif "5s" in choice:
            self.auto_refresh_sec = 5
        elif "10s" in choice:
            self.auto_refresh_sec = 10
        else:
            self.auto_refresh_sec = 0
            return

        self._schedule_auto_refresh()

    def _schedule_auto_refresh(self):
        if self.auto_refresh_sec > 0:
            self.start_scan()
            self.auto_refresh_job = self.after(self.auto_refresh_sec * 1000, self._schedule_auto_refresh)
