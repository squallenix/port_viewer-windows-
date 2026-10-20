# ⚡ Port Viewer • Windows Port & Process Manager

A high-performance, secure, and modern desktop application for Windows to inspect occupied network ports (TCP/UDP), identify the exact processes holding them, and safely terminate rogue or hung servers with a single click.

Built with Python, **CustomTkinter** (Windows 11 Fluent Dark UI), and **psutil** with native Win32 system API integration.

---

## 💡 Do Users Need Python Installed?

* **Regular Users (Running `.exe`)**: ❌ **NO Python needed.** 
  The standalone binary (`dist\PortViewer.exe`) contains the entire embedded runtime and dependencies. Anyone can simply double-click and run it on any Windows 10/11 machine.
* **Developers (Running from Source)**: ✔️ **Python 3.10+ required.**
  Only needed if you plan to edit the `.py` source files or compile a new executable using `build_exe.bat`.

---

## 📸 Key Features

- **🔍 One-Click Port Detection**: Instant scan of all active TCP/UDP ports, listening sockets, and established connections.
- **📊 Clickable Column Sorting**: Click any column header (`PROTO`, `PORT`, `LOCAL ADDRESS`, `STATUS`, `PROCESS NAME`, `PID`, `MEMORY`) to sort; click again to toggle between Ascending (`▲`) and Descending (`▼`). Numeric columns (`PORT`, `PID`, `MEMORY`) sort mathematically, not alphabetically.
- **⏹ One-Click Process Termination**: "Stop" button beside each occupied port to terminate hung servers (Node.js, Python, Apache, Docker, Vite, etc.) without opening Command Prompt or Task Manager.
- **⚡ Instant Real-Time Search**: Filter in real time as you type by Port Number (e.g., `3000`, `8080`, `5432`), Process Name (`node.exe`, `python.exe`), or PID.
- **🎛️ Filter Presets**: Instant tabs for **Listening Only (Servers)**, **All Ports**, **TCP Only**, and **UDP Only**.
- **🔄 Auto-Refresh**: Configurable background polling (`Off`, `3s`, `5s`, `10s`) using asynchronous background threads so the UI never freezes or stutters.
- **🛡️ Built-in Security Hardening**: Hardened against command injection, process hijacking, TOCTOU race conditions, and accidental Windows BSOD crashes.
- **📦 Single-File `.exe`**: Portable standalone executable requiring zero installation.

---

## 🛡️ Security Architecture & Anti-Hacking Hardening

Many port viewers run local web servers (e.g. `http://localhost:5000`) or invoke shell strings (`taskkill /F /PID %pid%`). These introduce critical vulnerabilities. Port Viewer is explicitly engineered to prevent these exploits:

| Attack Vector | Risk | Port Viewer Countermeasure |
| :--- | :--- | :--- |
| **Local Web CSRF / DNS Rebinding** | Malicious websites in the user's browser send `fetch()` requests against localhost to kill processes or abuse system ports. | **Zero Open Network Ports**: Port Viewer is a 100% native desktop GUI. It does not open any network socket, HTTP server, or listener. |
| **Command / Shell Injection (RCE)** | Special characters or malformed process names passed to `cmd.exe` or `powershell.exe`. | **Zero Shell Invocation**: Never uses `os.system()` or `shell=True`. Process enumeration and termination rely entirely on direct Windows kernel API calls (`OpenProcess`, `TerminateProcess`). |
| **Accidental BSOD / Crash** | Terminating Windows kernel processes (PID 0, PID 4, `csrss.exe`) triggers immediate Blue Screen of Death. | **Core Process Protection**: Hard-coded safety check that locks and blocks termination of critical Windows system processes. |
| **TOCTOU Race Condition** | A process exits and Windows recycles its PID before the user clicks Stop, killing an innocent new process. | **Process Timestamp Verification**: Scans record `create_time`. Before termination, the PID's creation timestamp is strictly verified against the recorded timestamp. |
| **PID Spoofing & Bounds** | Negative, invalid, or zero PIDs passed to APIs. | Strict integer validation (`isinstance(pid, int) and pid > 0`). |
| **Self-Termination** | Port Viewer accidentally terminating itself. | Self PID (`os.getpid()`) is protected. |
| **Privilege Escalation** | Inability to terminate system services without administrator permissions. | Built-in UAC elevation detection with clean `ShellExecuteW` elevation helper. |

---

## 🚀 Quick Start (Running on Windows)

### Option 1: Run the Standalone `.exe` (Easiest — No Python Required)
If you already have or built `PortViewer.exe`:
1. Navigate to `dist\PortViewer.exe` (or download it from Releases).
2. Double-click to launch immediately!

---

### Option 2: Build Your Own `.exe` (One-Click)
To package the repository into a fresh, portable `.exe`:
1. Double-click **`build_exe.bat`**.
2. The script will automatically:
   - Detect or initialize the virtual environment (`.venv`)
   - Install required dependencies (`requirements.txt`)
   - Generate multi-size application icons
   - Run PyInstaller and output `dist\PortViewer.exe`
3. You can now distribute `dist\PortViewer.exe` to any Windows user.

---

### Option 3: Run Directly from Source (One-Click)
If you have Python installed:
1. Double-click **`run.bat`**.
2. Automatically sets up the virtual environment, installs dependencies if needed, and starts the GUI.

---

### Option 4: Interactive Setup & Desktop Shortcut
Run **`setup.bat`** to:
1. Automatically initialize `.venv` and dependencies.
2. Run automated security and sorting test suites.
3. Provide a one-click option to create a **Windows Desktop Shortcut**.

---

### Option 5: Manual Command Line
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

## 📊 How Clickable Column Sorting Works

You can click any column in the table header to sort the entries dynamically:

| Column | Sort Type | Description |
| :--- | :--- | :--- |
| **`PROTO`** | Alphabetical | Sorts by protocol (`TCP` vs `UDP`). |
| **`PORT`** | Numerical | Sorts by local port number (e.g., `80` < `443` < `3000` < `8080`). |
| **`LOCAL ADDRESS`**| Address & Port | Sorts by IP address (`0.0.0.0`, `127.0.0.1`, etc.). |
| **`STATUS`** | Alphabetical | Groups by connection status (`LISTEN`, `ESTABLISHED`, `TIME_WAIT`). |
| **`PROCESS NAME`** | Alphabetical | Sorts case-insensitively by executable name. |
| **`PID`** | Numerical | Sorts by Process ID. |
| **`MEMORY`** | Numerical | Sorts by RAM usage in MB. |

* Click once to sort **Ascending** (`▲`).
* Click again to sort **Descending** (`▼`).
* Sorting state is preserved across manual refreshes and auto-polling intervals.

---

## 🧪 Automated Testing

Port Viewer includes automated test coverage verifying PID validation, BSOD protections, system process blacklisting, and multi-column sorting:

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
├── dist/
│   └── PortViewer.exe       # Standalone compiled executable (No Python required)
├── src/
│   ├── port_scanner.py      # Safe kernel-level socket & process query engine
│   ├── process_manager.py   # Secure termination with TOCTOU & PID validation
│   ├── security.py          # Critical system process blacklist & UAC helper
│   └── ui/
│       ├── app.py           # Main GUI window, controls, and event loop
│       ├── components.py    # Stat cards, confirmation dialogs, admin alerts
│       └── theme.py         # Modern dark-mode color scheme & status badges
├── tests/
│   └── test_port_viewer.py  # Unit tests for security, process logic, and sorting
├── build_exe.bat            # One-click PyInstaller single-file EXE builder
├── run.bat                  # One-click runner script from source
├── setup.bat                # Interactive installer with Desktop shortcut creation
├── generate_icon.py         # Icon asset generation script
├── requirements.txt         # Pinned production dependencies
└── main.py                  # High-DPI aware Windows application entry point
```

---

## 📄 License
MIT License. Open source and free for personal and commercial use.
