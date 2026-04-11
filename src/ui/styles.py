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
    "bg_primary": "#1a1a1a",      # Main background
    "bg_secondary": "#2d2d2d",    # Secondary background
    "bg_tertiary": "#3d3d3d",     # Tertiary background
    "fg_primary": "#ffffff",      # Main text
    "fg_secondary": "#cccccc",    # Secondary text
    
    # Accent colors
    "accent": "#4CAF50",          # Main accent (green)
    "accent_dark": "#388E3C",     # Darker accent
    "accent_light": "#81C784",    # Lighter accent
    
    # Status colors
    "success": "#00FF00",         # Success (bright green)
    "warning": "#FFA500",         # Warning (orange)
    "error": "#FF6B6B",           # Error (red)
    "info": "#87CEEB",            # Info (sky blue)
    
    # Component colors
    "header_bg": "#2d2d2d",
    "panel_bg": "#1a1a1a",
    "panel_border": "#4CAF50",
    "button_active": "#4CAF50",
    "button_inactive": "#666666",
    "console_bg": "#000000",
    "console_fg": "#00FF00",
}

# ═══════════════════════════════════════════════════════════════════════════
# Font Configuration - Docker-safe fonts
# ═══════════════════════════════════════════════════════════════════════════

# Use standard fonts available in all environments (Windows, Linux, Mac)
FONTS = {
    "title": ("Arial", 18, "bold"),
    "heading": ("Arial", 12, "bold"),
    "subheading": ("Arial", 10, "bold"),
    "normal": ("Arial", 10),
    "small": ("Arial", 9),
    "console": ("Courier New", 9),
    "console_mono": ("Courier", 9),
}

# ═══════════════════════════════════════════════════════════════════════════
# UI Configuration
# ═══════════════════════════════════════════════════════════════════════════

UI_CONFIG = {
    # Window settings
    "window_width": 1100,
    "window_height": 750,
    "window_title": "🤖 Voice Assistant",
    "always_on_top": True,
    
    # Padding & spacing
    "padding_lg": 20,
    "padding_md": 15,
    "padding_sm": 10,
    "padding_xs": 5,
    
    # Console settings
    "console_height": 20,
    "console_width": 60,
    "console_max_lines": 10000,
    
    # Buttons
    "button_height": 12,
    "button_width": 20,
    
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
