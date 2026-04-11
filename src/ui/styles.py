"""
UI Theme & Styles Configuration
Centralized color schemes and fonts for consistent look
Works with Docker environments (no local font assumptions)
"""

import os

# ═══════════════════════════════════════════════════════════════════════════
# Color Palette - Dark Professional Theme
# ═══════════════════════════════════════════════════════════════════════════

COLORS = {
    # Base colors
    "bg_primary": "#0f172a",      # Main background
    "bg_secondary": "#111827",    # Secondary background
    "bg_tertiary": "#1f2937",     # Tertiary background
    "bg_quaternary": "#273449",   # Elevated background
    "fg_primary": "#f8fafc",      # Main text
    "fg_secondary": "#cbd5e1",    # Secondary text
    "fg_muted": "#94a3b8",        # Muted text
    
    # Accent colors
    "accent": "#22c55e",          # Main accent (emerald)
    "accent_dark": "#16a34a",     # Darker accent
    "accent_light": "#86efac",    # Lighter accent
    "accent_blue": "#38bdf8",     # Secondary accent
    
    # Status colors
    "success": "#22c55e",         # Success
    "warning": "#f59e0b",         # Warning
    "error": "#f87171",           # Error
    "info": "#38bdf8",            # Info
    
    # Component colors
    "header_bg": "#0b1120",
    "panel_bg": "#111827",
    "panel_border": "#334155",
    "panel_shadow": "#020617",
    "button_active": "#22c55e",
    "button_inactive": "#334155",
    "console_bg": "#020617",
    "console_fg": "#cbd5e1",
    "input_bg": "#0b1220",
    "input_border": "#334155",
}

# ═══════════════════════════════════════════════════════════════════════════
# Font Configuration - Docker-safe fonts
# ═══════════════════════════════════════════════════════════════════════════

# Use standard fonts available in all environments (Windows, Linux, Mac)
FONTS = {
    "title": ("Segoe UI", 19, "bold"),
    "subtitle": ("Segoe UI", 10),
    "heading": ("Segoe UI", 12, "bold"),
    "subheading": ("Segoe UI", 10, "bold"),
    "normal": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "console": ("Consolas", 9),
    "console_mono": ("Consolas", 9),
}

# ═══════════════════════════════════════════════════════════════════════════
# UI Configuration
# ═══════════════════════════════════════════════════════════════════════════

UI_CONFIG = {
    # Window settings
    "window_width": 1240,
    "window_height": 820,
    "window_title": "🤖 Voice Assistant",
    "always_on_top": True,
    "min_width": 1120,
    "min_height": 760,
    
    # Padding & spacing
    "padding_lg": 22,
    "padding_md": 16,
    "padding_sm": 10,
    "padding_xs": 6,
    "section_gap": 14,
    
    # Console settings
    "console_height": 20,
    "console_width": 62,
    "console_max_lines": 10000,
    
    # Buttons
    "button_height": 12,
    "button_width": 22,
    
    # Response timeouts (for containerized environments)
    "response_timeout": 30,
    "gui_update_interval": 100,  # ms
}

# ═══════════════════════════════════════════════════════════════════════════
# Environment-based adjustments
# ═══════════════════════════════════════════════════════════════════════════

# Check if running in Docker/container
IS_CONTAINERIZED = os.getenv("DOCKER_CONTAINER", "false").lower() == "true"

if IS_CONTAINERIZED:
    # Adjust for container environments
    UI_CONFIG["response_timeout"] = 60  # Longer timeout in containers
    UI_CONFIG["console_max_lines"] = 5000  # Limit memory usage
    COLORS["console_fg"] = "#00FF00"  # Keep console visible in containers

# ═══════════════════════════════════════════════════════════════════════════
# Status Icons
# ═══════════════════════════════════════════════════════════════════════════

ICONS = {
    # Status indicators
    "sleep": "🔴",
    "awake": "🟢",
    "listening": "🎤",
    "processing": "⚙️",
    
    # Actions
    "wake": "🔊",
    "sleep_action": "😴",
    "send": "📤",
    "analyze": "🔬",
    "summarize": "📋",
    "help": "❓",
    "error": "❌",
    "success": "✓",
    "warning": "⚠️",
    "info": "ℹ️",
    "exit": "↪",
    
    # UI Elements
    "console": "💻",
    "settings": "⚙️",
    "menu": "☰",
    "pulse": "◉",
}

# ═══════════════════════════════════════════════════════════════════════════
# Quick Commands Configuration
# ═══════════════════════════════════════════════════════════════════════════

QUICK_COMMANDS = {
    "basic": [
        ("Open YouTube", "open youtube"),
        ("Open Google", "open google"),
        ("Search", "search for"),
        ("Help", "help"),
    ],
    "ai": [
        ("Analyze Page", "analyze this page"),
        ("Summarize", "summarize this page"),
        ("Key Points", "give me key points"),
        ("Analyze Code", "analyze code from file"),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
# Helper function to get config safely
# ═══════════════════════════════════════════════════════════════════════════

def get_color(color_name: str) -> str:
    """Get color by name, with fallback"""
    return COLORS.get(color_name, COLORS["fg_primary"])

def get_font(font_name: str) -> tuple:
    """Get font by name, with fallback"""
    return FONTS.get(font_name, FONTS["normal"])

def get_icon(icon_name: str) -> str:
    """Get icon by name, with fallback"""
    return ICONS.get(icon_name, "•")


def apply_ttk_theme(root) -> None:
    """Apply a consistent ttk theme to notebooks and tabs."""
    try:
        style = __import__("tkinter.ttk", fromlist=["Style"]).Style(root)
        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background=COLORS["bg_primary"],
            borderwidth=0,
            tabmargins=(0, 8, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["bg_tertiary"],
            foreground=COLORS["fg_secondary"],
            padding=(14, 8),
            borderwidth=0,
            focuscolor=COLORS["accent"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["bg_quaternary"])],
            foreground=[("selected", COLORS["fg_primary"])],
        )
    except Exception:
        # Theme setup is cosmetic; fall back to default if ttk styling fails.
        pass
