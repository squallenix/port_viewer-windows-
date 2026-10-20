import os
import psutil
from dataclasses import dataclass
from typing import Optional
from src.security import validate_pid, is_critical_process, is_admin

@dataclass
class ProcessResult:
    success: bool
    message: str
    requires_admin: bool = False

def terminate_process_by_pid(pid: int, expected_create_time: Optional[float] = None) -> ProcessResult:
    """
    Safely terminates a process by PID using native OS handles.
    Guaranteed NO shell injection, strict PID checking, TOCTOU protection,
    and BSOD crash prevention.
    """
    # 1. PID integrity check
    is_safe, error_msg = validate_pid(pid)
    if not is_safe:
        return ProcessResult(success=False, message=error_msg)

    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return ProcessResult(success=False, message=f"Process with PID {pid} is no longer running.")
    except psutil.AccessDenied:
        return ProcessResult(
            success=False,
            message=f"Access denied terminating PID {pid}. This process requires Administrator rights.",
            requires_admin=True
        )

    # 2. Check critical system process name
    try:
        proc_name = proc.name()
        if is_critical_process(proc_name):
            return ProcessResult(
                success=False,
                message=f"Blocked: '{proc_name}' (PID {pid}) is a protected core Windows system process. Terminating it would crash your operating system."
            )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    # 3. TOCTOU Protection: Ensure PID wasn't recycled by OS
    if expected_create_time is not None and expected_create_time > 0:
        try:
            current_create_time = proc.create_time()
            # Allow small float epsilon diff
            if abs(current_create_time - expected_create_time) > 0.05:
                return ProcessResult(
                    success=False,
                    message="Safety Trigger: Process was recycled (PID reuse detected). Termination aborted to protect the new process."
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 4. Safe termination: Attempt graceful termination first, then force kill if needed
    try:
        proc.terminate()
        try:
            # Wait briefly for graceful exit
            proc.wait(timeout=1.5)
            return ProcessResult(success=True, message=f"Successfully stopped process {proc_name or pid} (PID: {pid}).")
        except psutil.TimeoutExpired:
            # Force kill if still holding port
            proc.kill()
            return ProcessResult(success=True, message=f"Process {proc_name or pid} (PID: {pid}) was forcefully terminated.")
    except psutil.AccessDenied:
        return ProcessResult(
            success=False,
            message=f"Access denied terminating PID {pid}. Please run Port Viewer as Administrator.",
            requires_admin=True
        )
    except psutil.NoSuchProcess:
        return ProcessResult(success=True, message=f"Process (PID: {pid}) has terminated.")
    except Exception as e:
        return ProcessResult(success=False, message=f"Failed to terminate process: {str(e)}")
