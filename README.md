# ⚡ Port Viewer • Windows Port & Process Manager

A high-performance, secure, and modern desktop application for Windows to inspect occupied network ports (TCP/UDP), identify the exact processes holding them, and safely terminate rogue or hung servers with a single click.

Built with Python, **CustomTkinter** (Windows 11 Fluent UI), and **psutil** with native Win32 system integration.

---

## 📸 Key Features

- **🔍 One-Click Port Detection**: Instant scan of all active TCP/UDP ports, listening sockets, and established connections.
- **📊 Interactive Clickable Column Sorting**: Click any column header (`PROTO`, `PORT`, `LOCAL ADDRESS`, `STATUS`, `PROCESS NAME`, `PID`, `MEMORY`) to sort the list; click again to toggle between Ascending (`▲`) and Descending (`▼`).
- **⏹ Instant Process Termination**: "Stop" button beside each occupied port to terminate hung servers (Node.js, Python, Apache, Docker, etc.) without opening Command Prompt or Task Manager.
- **⚡ Instant Real-Time Search**: Filter in real time as you type by Port Number (e.g., `3000`, `8080`, `5432`), Process Name (`node.exe`, `python.exe`), or PID.
- **🎛️ Filter Presets**: Instant tabs for **Listening Only (Servers)**, **All Ports**, **TCP Only**, and **UDP Only**.
- **🔄 Auto-Refresh**: Configurable background polling (Off, 3s, 5s, 10s) with non-blocking threaded execution.
- **🛡️ Built-in Security & Safety**: Hardened against command injection, process hijacking, TOCTOU race conditions, and accidental Windows BSOD crashes.
- **📦 Single-File `.exe`**: Portable executable requiring zero installation.

---

## 🛡️ Security Architecture & Anti-Hacking Protections

Many open-source port viewers create local web interfaces (e.g., on `http://localhost:5000`) or invoke shell strings (`taskkill /F /PID %pid%`). These introduce serious security vulnerabilities. Port Viewer is specifically hardened against these attack vectors:

| Attack Vector | Risk | Port Viewer Countermeasure |
| :--- | :--- | :--- |
| **Local Web CSRF / DNS Rebinding** | Malicious websites in browser execute `fetch()` requests against localhost to kill processes or take over ports. | **Zero Open Network Ports**: Port Viewer is a 100% native desktop GUI. It does not open any network socket, HTTP server, or listener. |
| **Command Injection (RCE)** | Special characters or malformed process names passed to `cmd.exe` or `powershell.exe`. | **Zero Shell Invocation**: Never uses `os.system()` or `shell=True`. Process enumeration and termination rely entirely on direct Windows kernel API calls (`OpenProcess`, `TerminateProcess`). |
| **Accidental BSOD / Crash** | Terminating Windows kernel processes (PID 0, PID 4, `csrss.exe`) triggers immediate Blue Screen of Death. | **Core Process Protection**: Hard-coded safety check that locks and blocks termination of critical Windows system processes. |
| **TOCTOU Race Condition** | A process exits and Windows recycles its PID before the user clicks Stop, killing an innocent new process. | **Process Timestamp Verification**: Scans record `create_time`. Before termination, the PID's creation timestamp is strictly verified against the recorded timestamp. |
| **PID Spoofing & Bounds** | Negative, invalid, or zero PIDs passed to APIs. | Strict integer validation (`isinstance(pid, int) and pid > 0`). |
| **Self-Termination** | Port Viewer accidentally terminating itself. | Self PID (`os.getpid()`) is protected. |
| **Privilege Escalation** | Inability to terminate system services without administrator permissions. | Built-in UAC elevation detection with clean `ShellExecuteW` elevation helper. |

---

## 🚀 Quick Start (Running on Windows)

### Method 1: One-Click Runner (No installation required)
If you have Python installed:
1. Double-click **`run.bat`**.
2. The script will automatically create a virtual environment (`.venv`), install requirements, and start the app.

---

### Method 2: Convert to Standalone `.exe`
To package the entire project into a single, portable `PortViewer.exe` that can be shared with anyone:
1. Double-click **`build_exe.bat`**.
2. Once the build finishes, you will find your executable at:
   ```
   dist\PortViewer.exe
   ```
3. You can copy `PortViewer.exe` to any Windows computer and run it without needing Python installed!

---

### Method 3: One-Click Setup & Desktop Shortcut
Run **`setup.bat`** to:
- Automatically initialize `.venv`
- Install dependencies
- Run automated security test suite
- Optionally place a **Desktop Shortcut** to launch Port Viewer anytime.

---

### Method 4: Manual Command Line
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## 🧪 Automated Testing

Port Viewer includes automated test coverage verifying PID validation, BSOD protections, system process blacklisting, and network connection scanning:

```powershell
.\.venv\Scripts\python -m unittest tests\test_port_viewer.py
```

---

## 📁 Project Structure

```
port_viewer/
├── assets/
│   ├── icon.ico             # High-resolution multi-size Windows icon
│   └── icon.png             # Application logo
├── src/
│   ├── port_scanner.py      # Safe kernel-level socket & process query engine
│   ├── process_manager.py   # Secure termination with TOCTOU & PID validation
│   ├── security.py          # Critical system process blacklist & UAC helper
│   └── ui/
│       ├── app.py           # Main GUI window, controls, and event loop
│       ├── components.py    # Stat cards, confirmation dialogs, admin alerts
│       └── theme.py         # Modern dark-mode color scheme & status badges
├── tests/
│   └── test_port_viewer.py  # Unit tests for security & process logic
├── build_exe.bat            # One-click PyInstaller single-file EXE builder
├── run.bat                  # One-click runner script from source
├── setup.bat                # Interactive installer with Desktop shortcut creation
├── generate_icon.py         # Icon asset generation script
├── requirements.txt         # Pinned production dependencies
└── main.py                  # DPI-aware Windows application entry point
```

---

## 📄 License
MIT License. Open source and free for personal and commercial use.
