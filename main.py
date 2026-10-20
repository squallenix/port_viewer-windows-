import os
import sys
import ctypes

# Enable high DPI scaling on Windows for crystal clear text
try:
    if os.name == 'nt':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ui.app import PortViewerApp

def main():
    try:
        app = PortViewerApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            import tkinter.messagebox as mb
            mb.showerror("Port Viewer Error", f"An unexpected error occurred:\n{str(e)}")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
