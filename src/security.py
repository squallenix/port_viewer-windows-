import os
import sys
import ctypes
from typing import Tuple, Optional

# Core critical Windows processes whose termination would immediately trigger BSOD or critical crash
CRITICAL_SYSTEM_PROCESSES = {
    "system",
    "system idle process",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "winlogon.exe",
    "fontdrvhost.exe",
    "dwm.exe",
}

# Processes that require extra user caution
SENSITIVE_PROCESSES = {
    "svchost.exe",
    "explorer.exe",
    "spoolsv.exe",
    "taskhostw.exe",
    "sihost.exe",
}

def is_admin() -> bool:
    """Check if the current process has Windows Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def restart_as_admin():
    """Relaunches the current application with elevated Administrator privileges via UAC prompt."""
    if is_admin():
        return True

    # Use ShellExecuteW directly with 'runas' verb (safe Windows native elevation)
    # Strictly pass the current executable and script without shell expansion
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller executable
            executable = sys.executable
            params = ""
        else:
            executable = sys.executable
            params = f'"{os.path.abspath(sys.argv[0])}"'
            if len(sys.argv) > 1:
                params += " " + " ".join(f'"{arg}"' for arg in sys.argv[1:])

        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            params,
            None,
            1  # SW_SHOWNORMAL
        )
        if result > 32:
            sys.exit(0)
            return True
        return False
    except Exception as e:
        return False

def validate_pid(pid: int) -> Tuple[bool, str]:
    """
    Validates PID to prevent system damage, self-termination, or invalid inputs.
    Returns: (is_safe, error_or_warning_message)
    """
    if not isinstance(pid, int) or pid < 0:
        return False, "Invalid PID: must be a positive integer."

    # PID 0 is System Idle, PID 4 is NT Kernel / System
    if pid in (0, 4):
        return False, f"PID {pid} is a protected core Windows kernel process (BSOD risk)."

    # Protect own process from accidental self-termination
    if pid == os.getpid():
        return False, f"PID {pid} is this Port Viewer application itself."

    return True, ""

def is_critical_process(process_name: str) -> bool:
    """Returns True if the process is a protected Windows core process."""
    if not process_name:
        return False
    return process_name.strip().lower() in CRITICAL_SYSTEM_PROCESSES

def is_sensitive_process(process_name: str) -> bool:
    """Returns True if the process is a Windows service that needs extra caution."""
    if not process_name:
        return False
    return process_name.strip().lower() in SENSITIVE_PROCESSES
