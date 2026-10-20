# UI Color constants and styling definitions

COLORS = {
    "bg_dark": "#0F172A",          # Slate 900
    "card_bg": "#1E293B",          # Slate 800
    "card_border": "#334155",      # Slate 700
    "hover_bg": "#26334D",
    
    "primary": "#3B82F6",          # Blue 500
    "primary_hover": "#2563EB",    # Blue 600
    
    "danger": "#EF4444",           # Red 500
    "danger_hover": "#DC2626",     # Red 600
    
    "success": "#10B981",          # Emerald 500
    "warning": "#F59E0B",          # Amber 500
    "purple": "#8B5CF6",           # Purple 500
    "info": "#06B6D4",             # Cyan 500
    
    "text_main": "#F8FAFC",        # Slate 50
    "text_muted": "#94A3B8",       # Slate 400
    "text_dim": "#64748B",         # Slate 500
    
    "status_listen": "#10B981",
    "status_established": "#3B82F6",
    "status_wait": "#F59E0B",
    "status_udp": "#8B5CF6",
    "status_other": "#64748B",
}

def get_status_color(status: str) -> str:
    status_upper = status.upper() if status else ""
    if "LISTEN" in status_upper:
        return COLORS["status_listen"]
    elif "ESTABLISHED" in status_upper:
        return COLORS["status_established"]
    elif "WAIT" in status_upper or "CLOSE" in status_upper:
        return COLORS["status_wait"]
    elif "UDP" in status_upper or "ACTIVE" in status_upper:
        return COLORS["status_udp"]
    return COLORS["status_other"]
