import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
from src.ui.theme import COLORS, get_status_color
from src.port_scanner import PortItem
from src.security import restart_as_admin

class StatCard(ctk.CTkFrame):
    """Modern dashboard stat card."""
    def __init__(self, master, title: str, value: str = "0", icon: str = "", subtext: str = ""):
        super().__init__(master, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["card_border"])
        
        self.grid_columnconfigure(1, weight=1)

        # Icon
        self.icon_lbl = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=24), width=40
        )
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=10)

        # Value
        self.val_lbl = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_main"], anchor="w"
        )
        self.val_lbl.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(8, 0))

        # Title
        self.title_lbl = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"], anchor="w"
        )
        self.title_lbl.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 8))

    def update_value(self, value: str):
        self.val_lbl.configure(text=value)


class ConfirmStopDialog(ctk.CTkToplevel):
    """
    Security Confirmation Dialog before terminating any process.
    Prevents accidental clicks and provides full context (PID, Port, Path).
    """
    def __init__(self, parent, item: PortItem, on_confirm: Callable[[], None]):
        super().__init__(parent)
        self.item = item
        self.on_confirm = on_confirm

        self.title("Confirm Termination")
        self.geometry("520x360")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_dark"])

        # Center dialog relative to parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 260
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 180
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._build_ui()
        self.grab_set()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12, border_width=1, border_color=COLORS["card_border"])
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        header_text = "⚠️ Stop Running Process?"
        header_color = COLORS["danger"]
        if self.item.is_sensitive:
            header_text = "⚠️ Caution: Windows Service"
            header_color = COLORS["warning"]

        header_lbl = ctk.CTkLabel(
            main_frame, text=header_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=header_color
        )
        header_lbl.pack(pady=(16, 8), padx=16, anchor="w")

        info_text = (
            f"Are you sure you want to stop this process?\n"
            f"Any active network connections on port {self.item.local_port} will be closed immediately."
        )
        sub_lbl = ctk.CTkLabel(
            main_frame, text=info_text,
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
            justify="left", anchor="w"
        )
        sub_lbl.pack(fill="x", padx=16, pady=(0, 12))

        # Details Card
        detail_card = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_dark"], corner_radius=8, border_width=1, border_color=COLORS["card_border"])
        detail_card.pack(fill="x", padx=16, pady=6)

        rows = [
            ("Process Name:", f"{self.item.process_name}"),
            ("Process PID:", f"{self.item.pid}"),
            ("Occupied Port:", f"{self.item.local_port} ({self.item.protocol})"),
            ("Status:", f"{self.item.status}"),
            ("Path:", f"{self.item.process_path or 'N/A'}")
        ]

        for i, (k, v) in enumerate(rows):
            k_lbl = ctk.CTkLabel(
                detail_card, text=k, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_muted"], width=110, anchor="w"
            )
            k_lbl.grid(row=i, column=0, padx=(12, 6), pady=3, sticky="w")
            
            # Truncate long paths
            display_v = v if len(v) < 45 else v[:20] + "..." + v[-22:]
            v_lbl = ctk.CTkLabel(
                detail_card, text=display_v, font=ctk.CTkFont(size=12, family="Consolas"),
                text_color=COLORS["text_main"], anchor="w"
            )
            v_lbl.grid(row=i, column=1, padx=(0, 12), pady=3, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(16, 12), side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", fg_color=COLORS["card_border"],
            hover_color=COLORS["hover_bg"], text_color=COLORS["text_main"],
            width=100, command=self.destroy
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        confirm_btn = ctk.CTkButton(
            btn_frame, text="⏹ Terminate Process", fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"), width=160,
            command=self._confirm
        )
        confirm_btn.pack(side="right")

    def _confirm(self):
        self.destroy()
        self.on_confirm()


class AdminNoticeDialog(ctk.CTkToplevel):
    """Dialog displayed when an action requires Administrator rights."""
    def __init__(self, parent, message: str):
        super().__init__(parent)
        self.title("Administrator Permissions Required")
        self.geometry("460x220")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_dark"])

        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 230
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12, border_width=1, border_color=COLORS["card_border"])
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        title_lbl = ctk.CTkLabel(
            frame, text="🛡️ Elevation Required", font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["warning"]
        )
        title_lbl.pack(pady=(16, 6), padx=16, anchor="w")

        msg_lbl = ctk.CTkLabel(
            frame, text=message, font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"], justify="left", wraplength=400
        )
        msg_lbl.pack(padx=16, pady=(0, 16), anchor="w")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(8, 8), side="bottom")

        close_btn = ctk.CTkButton(
            btn_frame, text="Dismiss", fg_color=COLORS["card_border"],
            hover_color=COLORS["hover_bg"], width=90, command=self.destroy
        )
        close_btn.pack(side="right", padx=(8, 0))

        restart_btn = ctk.CTkButton(
            btn_frame, text="Relaunch as Admin", fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], font=ctk.CTkFont(weight="bold"),
            command=self._elevate
        )
        restart_btn.pack(side="right")
        self.grab_set()

    def _elevate(self):
        self.destroy()
        restart_as_admin()
