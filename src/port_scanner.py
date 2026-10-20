import socket
import psutil
from dataclasses import dataclass
from typing import List, Optional
from src.security import is_critical_process, is_sensitive_process

@dataclass
class PortItem:
    protocol: str              # 'TCP' or 'UDP'
    local_ip: str              # e.g. '0.0.0.0', '127.0.0.1'
    local_port: int            # e.g. 3000
    remote_ip: str             # e.g. '192.168.1.5' or ''
    remote_port: Optional[int] # e.g. 443 or None
    status: str                # e.g. 'LISTEN', 'ESTABLISHED'
    pid: Optional[int]         # Process ID
    process_name: str          # e.g. 'node.exe'
    process_path: str          # e.g. 'C:\Program Files\nodejs\node.exe'
    create_time: float         # Process creation time for TOCTOU verification
    memory_mb: float           # Memory consumption in MB
    is_critical: bool          # Protected system process
    is_sensitive: bool         # Sensitive Windows service

def scan_ports(filter_listening_only: bool = False) -> List[PortItem]:
    """
    Scans all network connections and correlates them with processes.
    Safe, read-only kernel inspection using psutil native Win32 API bindings.
    """
    items: List[PortItem] = []
    
    # Process cache to avoid querying psutil.Process multiple times for the same PID
    process_cache = {}

    try:
        # psutil.net_connections queries TCP and UDP without external shell calls
        connections = psutil.net_connections(kind='inet')
    except Exception as e:
        # Fallback or error return
        return items

    for conn in connections:
        # Determine protocol
        proto = "TCP" if conn.type == socket.SOCK_STREAM else ("UDP" if conn.type == socket.SOCK_DGRAM else str(conn.type))
        
        status = conn.status if conn.status else ("ACTIVE" if proto == "UDP" else "UNKNOWN")

        # If user selected listening only, filter
        if filter_listening_only and status != "LISTEN":
            continue

        local_ip = conn.laddr.ip if conn.laddr else ""
        local_port = conn.laddr.port if conn.laddr else 0
        
        remote_ip = conn.raddr.ip if conn.raddr else ""
        remote_port = conn.raddr.port if conn.raddr else None
        
        pid = conn.pid
        proc_name = "Unknown"
        proc_path = ""
        create_time = 0.0
        memory_mb = 0.0
        is_crit = False
        is_sens = False

        if pid is not None and pid > 0:
            if pid in process_cache:
                proc_info = process_cache[pid]
            else:
                try:
                    p = psutil.Process(pid)
                    p_name = p.name()
                    try:
                        p_path = p.exe()
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        p_path = "Access Denied (System Service)"
                    
                    try:
                        c_time = p.create_time()
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        c_time = 0.0

                    try:
                        mem = p.memory_info().rss / (1024 * 1024)
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        mem = 0.0

                    proc_info = {
                        "name": p_name,
                        "path": p_path,
                        "create_time": c_time,
                        "memory_mb": round(mem, 1),
                        "is_critical": is_critical_process(p_name),
                        "is_sensitive": is_sensitive_process(p_name),
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    proc_info = {
                        "name": "Access Denied / System",
                        "path": "",
                        "create_time": 0.0,
                        "memory_mb": 0.0,
                        "is_critical": False,
                        "is_sensitive": False,
                    }
                process_cache[pid] = proc_info

            proc_name = proc_info["name"]
            proc_path = proc_info["path"]
            create_time = proc_info["create_time"]
            memory_mb = proc_info["memory_mb"]
            is_crit = proc_info["is_critical"]
            is_sens = proc_info["is_sensitive"]
        elif pid == 0:
            proc_name = "System Idle / TIME_WAIT"
            is_crit = True

        items.append(PortItem(
            protocol=proto,
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            status=status,
            pid=pid,
            process_name=proc_name,
            process_path=proc_path,
            create_time=create_time,
            memory_mb=memory_mb,
            is_critical=is_crit,
            is_sensitive=is_sens,
        ))

    # Sort ports in ascending order
    items.sort(key=lambda x: (x.local_port, x.protocol))
    return items
