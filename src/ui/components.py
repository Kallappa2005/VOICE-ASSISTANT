"""
UI Components
=============
Reusable tkinter widget factory functions.

All widgets share a consistent dark-theme color palette defined in COLORS.
Import individual factory functions as needed:

    from src.ui.components import make_input_field, make_button, make_output_console
"""

import tkinter as tk
from tkinter import scrolledtext

# ── Color palette ─────────────────────────────────────────────────────────────
COLORS: dict[str, str] = {
    'bg':           '#1e1e2e',   # main window background
    'surface':      '#2d2d44',   # card / panel surfaces
    'border':       '#3d3d5c',   # subtle borders
    'primary':      '#7c3aed',   # purple accent (send button, focus ring)
    'success':      '#059669',   # green (voice button)
    'danger':       '#dc2626',   # red (error states)
    'text':         '#e2e8f0',   # primary text
    'text_dim':     '#6b7280',   # secondary / placeholder text
    'input_bg':     '#111827',   # text-entry background
    'console_bg':   '#0f0f1a',   # output console background
}


# ── Widget factories ──────────────────────────────────────────────────────────

def make_input_field(parent: tk.Widget, width: int = 60) -> tk.Entry:
    """
    Create a styled single-line text input field.

    Args:
        parent (tk.Widget): Parent container.
        width  (int):       Character width hint.

    Returns:
        tk.Entry: Configured input widget.
    """
    entry = tk.Entry(
        parent,
        width=width,
        bg=COLORS['input_bg'],
        fg=COLORS['text'],
        insertbackground=COLORS['primary'],
        font=('Consolas', 12),
        relief='flat',
        bd=0,
        highlightthickness=2,
        highlightcolor=COLORS['primary'],
        highlightbackground=COLORS['border'],
    )
    return entry


def make_button(parent: tk.Widget, text: str, command,
                color: str = '#7c3aed',
                padx: int = 16, pady: int = 6) -> tk.Button:
    """
    Create a styled action button with hover highlight.

    Args:
        parent  (tk.Widget): Parent container.
        text    (str):       Label shown on button.
        command (callable):  Click callback.
        color   (str):       Hex background color.
        padx    (int):       Horizontal internal padding.
        pady    (int):       Vertical internal padding.

    Returns:
        tk.Button: Configured button widget.
    """
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg='#ffffff',
        font=('Consolas', 11, 'bold'),
        relief='flat',
        bd=0,
        padx=padx,
        pady=pady,
        cursor='hand2',
        activebackground=_darken(color, 0.80),
        activeforeground='#ffffff',
    )
    # Subtle hover: lighten on enter, restore on leave
    btn.bind('<Enter>', lambda _e: btn.config(bg=_lighten(color, 1.15)))
    btn.bind('<Leave>', lambda _e: btn.config(bg=color))
    return btn


def make_output_console(parent: tk.Widget,
                         height: int = 28) -> scrolledtext.ScrolledText:
    """
    Create a read-only, auto-scrolling output console.

    Consumers must temporarily set state='normal' before inserting text,
    then restore state='disabled':

        console.config(state='normal')
        console.insert('end', 'message\\n')
        console.see('end')
        console.config(state='disabled')

    Args:
        parent (tk.Widget): Parent container.
        height (int):       Visible row count.

    Returns:
        scrolledtext.ScrolledText: Configured read-only log widget.
    """
    console = scrolledtext.ScrolledText(
        parent,
        height=height,
        bg=COLORS['console_bg'],
        fg=COLORS['text'],
        font=('Consolas', 10),
        relief='flat',
        bd=0,
        wrap='word',
        state='disabled',
        highlightthickness=1,
        highlightbackground=COLORS['border'],
        selectbackground=COLORS['primary'],
        selectforeground='#ffffff',
        padx=10,
        pady=10,
        cursor='arrow',
    )
    return console


def make_label(parent: tk.Widget, text: str,
               font_size: int = 11,
               color: str | None = None,
               bold: bool = False) -> tk.Label:
    """
    Create a dark-themed text label.

    Args:
        parent    (tk.Widget): Parent container.
        text      (str):       Label text.
        font_size (int):       Font point size.
        color     (str | None): Foreground color (default: palette text).
        bold      (bool):      Use bold weight.

    Returns:
        tk.Label: Configured label widget.
    """
    weight = 'bold' if bold else 'normal'
    return tk.Label(
        parent,
        text=text,
        bg=COLORS['bg'],
        fg=color or COLORS['text'],
        font=('Consolas', font_size, weight),
    )


def make_separator(parent: tk.Widget) -> tk.Frame:
    """Return a 1-px horizontal divider line."""
    return tk.Frame(parent, bg=COLORS['border'], height=1)


# ── Internal color utilities ──────────────────────────────────────────────────

def _parse_hex(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _to_hex(r: int, g: int, b: int) -> str:
    return f'#{r:02x}{g:02x}{b:02x}'


def _darken(hex_color: str, factor: float = 0.80) -> str:
    r, g, b = _parse_hex(hex_color)
    return _to_hex(int(r * factor), int(g * factor), int(b * factor))


def _lighten(hex_color: str, factor: float = 1.15) -> str:
    r, g, b = _parse_hex(hex_color)
    return _to_hex(
        min(255, int(r * factor)),
        min(255, int(g * factor)),
        min(255, int(b * factor)),
    )
